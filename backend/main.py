from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import datetime
import logging
import json

import models
from database import engine, SessionLocal
from nlp_processor import StyleProcessorLegacy
from services.transcription_service import TranscriptionService
from services.style_analyzer import StyleAnalyzer
from services.style_expert_engine import FakeAIRulesEngine
from schemas import ProcessTextRequest, ToneRequest, SaveDocumentRequest

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("gema-backend")

# Inicializar Base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar Servicios
style_processor_legacy = StyleProcessorLegacy()  # Fallback para tonos sin StyleProfile
fake_ai_engine = FakeAIRulesEngine()              # Motor activo (Fase 3)
transcription_service = TranscriptionService("model_es")
style_analyzer = StyleAnalyzer()

# Rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DIR = os.path.join(BASE_DIR, "local_history_vault")
os.makedirs(VAULT_DIR, exist_ok=True)

# Directorio absoluto para archivos temporales de audio (nunca relativo al CWD)
TEMP_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI(title="Gema - STT Backend (Refactored)")

app.add_middleware(
    CORSMiddleware,
    # Restringido al origen del frontend. Añadir dominios de producción aquí si se despliega.
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root() -> dict:
    return {"status": "ok", "message": "Gema STT Backend Running (Secured)"}


# ---------------------------------------------------------------------------
# WORKER DE FONDO
# Se ejecuta DESPUÉS de que la respuesta HTTP 202 ya fue enviada al cliente.
# Tiene su propia sesión de BD para no interferir con el ciclo de vida del
# request original.
# ---------------------------------------------------------------------------
async def process_audio_background(
    job_id: str,
    temp_input_path: str,
    temp_wav_path: str,
) -> None:
    db = SessionLocal()
    try:
        job = db.query(models.JobHistory).filter(models.JobHistory.id == job_id).first()
        if not job:
            logger.error(f"[BG] Job {job_id} no encontrado en BD — abortando worker.")
            return

        logger.info(f"[BG] Iniciando transcripción para job {job_id} ({job.filename})")
        transcription_real = await transcription_service.process_audio(temp_input_path, temp_wav_path)

        job.transcription = transcription_real
        job.status = "completed"
        db.commit()
        logger.info(f"[BG] Job {job_id} completado y persistido.")

    except Exception as e:
        logger.error(f"[BG] Fallo en job {job_id}: {e}")
        # Intentamos marcar el error en BD para que el frontend pueda detectarlo
        try:
            job = db.query(models.JobHistory).filter(models.JobHistory.id == job_id).first()
            if job:
                job.status = "error"
                job.transcription = f"Error en procesamiento: {str(e)}"
                db.commit()
        except Exception as db_err:
            logger.error(f"[BG] No se pudo actualizar el estado de error en BD: {db_err}")

    finally:
        db.close()
        # Limpieza de temporales después del procesamiento
        for path in [temp_input_path, temp_wav_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as e:
                    logger.error(f"[BG] Fuga de disco en job {job_id}: {path} — {e}")

# ---------------------------------------------------------------------------
# ENDPOINT DE TRANSCRIPCIÓN (Patrón Async Request-Reply)
# Responde 202 Accepted en milisegundos. El procesamiento pesado ocurre
# en segundo plano, sin bloquear al cliente ni al Event Loop.
# ---------------------------------------------------------------------------
@app.post("/api/transcribe/file", status_code=202)
async def transcribe_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> dict:

    # --- Validación estricta temprana ---
    if not file.content_type or not file.content_type.startswith("audio/"):
        logger.warning(f"MIME inválido o ausente: {file.filename} ({file.content_type})")
        raise HTTPException(status_code=400, detail="El tipo MIME no corresponde a un audio.")

    allowed_extensions = {'.mp3', '.wav', '.ogg', '.opus', '.m4a', '.webm', '.aac', '.flac'}
    raw_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    file_ext = "".join(c for c in raw_ext if c.isalnum() or c == ".").lower()
    if not file_ext or file_ext not in allowed_extensions:
        logger.warning(f"Extensión no permitida o vacía: '{file_ext}' en '{file.filename}'")
        raise HTTPException(status_code=400, detail="Extensión de archivo no permitida.")

    unique_id = str(uuid.uuid4())
    temp_input_path = os.path.join(TEMP_DIR, f"temp_{unique_id}{file_ext}")
    temp_wav_path   = os.path.join(TEMP_DIR, f"temp_{unique_id}_converted.wav")

    # I/O rápido: guardamos el archivo y liberamos el descriptor de FastAPI
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.close()

    # Registro en BD con estado inicial "pending"
    db_job = models.JobHistory(
        filename=file.filename,
        original_format=file_ext.lstrip("."),
        status="pending",
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    logger.info(f"Job {db_job.id} encolado para '{file.filename}' — respondiendo 202.")

    # Delegamos el trabajo pesado: se ejecutará DESPUÉS de enviar la respuesta
    background_tasks.add_task(
        process_audio_background,
        job_id=db_job.id,
        temp_input_path=temp_input_path,
        temp_wav_path=temp_wav_path,
    )

    # Liberamos al cliente instantáneamente
    return {
        "message": "Audio recibido y procesando en segundo plano.",
        "job_id": db_job.id,
        "status": "pending",
    }


# ---------------------------------------------------------------------------
# ENDPOINT DE POLLING
# El frontend consulta este endpoint cada N segundos para saber si el
# job ya cambió de "pending" a "completed" o "error".
# ---------------------------------------------------------------------------
@app.get("/api/transcribe/status/{job_id}")
def get_transcription_status(job_id: str, db: Session = Depends(get_db)) -> dict:
    job = db.query(models.JobHistory).filter(models.JobHistory.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")
    return {
        "job_id": job.id,
        "status": job.status,          # "pending" | "completed" | "error"
        "transcription": job.transcription,
    }

@app.post("/api/process-text")
def process_text(request: ProcessTextRequest, db: Session = Depends(get_db)) -> dict:
    """
    Motor activo: FakeAIRulesEngine (Fase 3).
    Fallback: StyleProcessorLegacy si no existe StyleProfile en DB para el tono.
    Responde con EngineResponse (backward-compatible: siempre incluye corrected_text).
    """
    # ── Cargar StyleProfile del tono ────────────────────────────────────────
    profile_row = db.query(models.StyleProfile).filter(
        models.StyleProfile.tone_name == request.tone_name
    ).first()

    # ── Fallback legacy si no hay perfil en DB ──────────────────────────────
    if not profile_row:
        logger.info(f"[process-text] Sin StyleProfile para '{request.tone_name}' — usando fallback legacy.")
        tone_settings = db.query(models.ToneSettings).filter(
            models.ToneSettings.tone_name == request.tone_name
        ).first()
        reference_text = tone_settings.reference_text if tone_settings else ""
        corrected_text = style_processor_legacy.process_text(
            request.raw_text, request.tone_name, reference_text
        )
        return {"corrected_text": corrected_text, "suggestions": [], "alerts": [], "style_report": {}}

    # ── Motor experto: cargar tesauro y palabras prohibidas ─────────────────
    profile_dict = {
        "avg_sentence_len":    profile_row.avg_sentence_len,
        "max_sentence_len":    profile_row.max_sentence_len,
        "ttr_target":          profile_row.ttr_target,
        "adjective_density":   profile_row.adjective_density,
        "flesch_target":       profile_row.flesch_target,
        "short_sentence_ratio": profile_row.short_sentence_ratio,
        "reference_author":    profile_row.reference_author,
        "style_display_name":  profile_row.style_display_name,
        "forbidden_words":     profile_row.forbidden_words,
        "preferred_structures": profile_row.preferred_structures,
        "compound_replacements": profile_row.compound_replacements,
    }

    thesaurus_rows = db.query(models.LiteraryThesaurus).filter(
        models.LiteraryThesaurus.tone_name == request.tone_name
    ).order_by(models.LiteraryThesaurus.priority.desc()).all()

    thesaurus_entries = [
        {
            "source_lemma": row.source_lemma,
            "target_word":  row.target_word,
            "pos_tag":      row.pos_tag,
            "intensity":    row.intensity,
            "context_hint": row.context_hint,
            "priority":     row.priority,
        }
        for row in thesaurus_rows
    ]

    prohibited_rows = db.query(models.ProhibitedWord).filter(
        models.ProhibitedWord.tone_name == request.tone_name
    ).all()

    prohibited_words = [
        {"word": row.word, "reason": row.reason, "suggestion": row.suggestion}
        for row in prohibited_rows
    ]

    # ── Ejecutar motor ───────────────────────────────────────────────────────
    result = fake_ai_engine.analyze_and_fix(
        text=request.raw_text,
        tone_name=request.tone_name,
        style_profile=profile_dict,
        thesaurus_entries=thesaurus_entries,
        prohibited_words=prohibited_words,
    )

    return {
        "corrected_text": result.corrected_text,
        "suggestions":    [vars(s) for s in result.suggestions],
        "alerts":         [vars(a) for a in result.alerts],
        "style_report":   result.style_report,
    }


# ---------------------------------------------------------------------------
# ENDPOINTS NUEVOS — Motor Estilométrico Zero-IA (Fase 2)
# ---------------------------------------------------------------------------

@app.post("/api/analyze-text")
def analyze_text(request: ProcessTextRequest, db: Session = Depends(get_db)) -> dict:
    """
    Devuelve métricas estilométricas puras del texto sin modificarlo.
    Útil para el panel de diagnóstico y para pruebas del motor.
    """
    # Cargar perfil del tono desde la DB
    profile_row = db.query(models.StyleProfile).filter(
        models.StyleProfile.tone_name == request.tone_name
    ).first()

    profile_dict = None
    if profile_row:
        profile_dict = {
            "avg_sentence_len":    profile_row.avg_sentence_len,
            "max_sentence_len":    profile_row.max_sentence_len,
            "ttr_target":          profile_row.ttr_target,
            "adjective_density":   profile_row.adjective_density,
            "flesch_target":       profile_row.flesch_target,
            "short_sentence_ratio": profile_row.short_sentence_ratio,
            "reference_author":    profile_row.reference_author,
            "style_display_name":  profile_row.style_display_name,
        }

    metrics = style_analyzer.analyze(request.raw_text, profile_dict)

    return {
        "sentence_count":         metrics.sentence_count,
        "word_count":             metrics.word_count,
        "unique_words":           metrics.unique_words,
        "avg_sentence_len":       metrics.avg_sentence_len,
        "max_sentence_len":       metrics.max_sentence_len,
        "sentence_len_stddev":    metrics.sentence_len_stddev,
        "short_sentence_ratio":   metrics.short_sentence_ratio,
        "ttr":                    metrics.ttr,
        "adjective_density":      metrics.adjective_density,
        "adverb_count":           metrics.adverb_count,
        "mente_adverb_count":     metrics.mente_adverb_count,
        "flesch_score":           metrics.flesch_score,
        "fernandez_huerta":       metrics.fernandez_huerta,
        "avg_syllables_per_word": metrics.avg_syllables_per_word,
        "dominant_verb_tense":    metrics.dominant_verb_tense,
        "pos_sequences_top3":     metrics.pos_sequences_top3,
        "compound_patterns":      metrics.compound_patterns,
        "alignment_score":        metrics.alignment_score,
        "profile":                metrics.profile_data,
    }


@app.get("/api/engine/status")
def engine_status(db: Session = Depends(get_db)) -> dict:
    """
    Estado del motor: versión, tonos con perfil en DB, conteo del tesauro.
    """
    profiles = db.query(models.StyleProfile).all()
    thesaurus_count = db.query(models.LiteraryThesaurus).count()
    prohibited_count = db.query(models.ProhibitedWord).count()
    dna_count = db.query(models.LiteraryDNA).count()

    return {
        "engine_version": "2.0-stylometric",
        "engine_mode": "expert-rules",  # FakeAIRulesEngine activo (Fase 3)
        "profiles_loaded": [
            {
                "tone_name": p.tone_name,
                "display_name": p.style_display_name,
                "reference_author": p.reference_author,
            }
            for p in profiles
        ],
        "thesaurus_entries": thesaurus_count,
        "prohibited_words":  prohibited_count,
        "literary_dna_records": dna_count,
    }

@app.get("/api/history")
def get_history(db: Session = Depends(get_db)) -> list:
    jobs = db.query(models.JobHistory).order_by(models.JobHistory.created_at.desc()).all()
    return [{
        "id": str(job.id),
        "filename": job.filename,
        "transcription": job.transcription,
        "createdAt": job.created_at.isoformat()
    } for job in jobs]

@app.post("/api/tones")
def save_tone(request: ToneRequest, db: Session = Depends(get_db)) -> dict:
    tone = db.query(models.ToneSettings).filter(models.ToneSettings.tone_name == request.tone_name).first()
    if tone:
        tone.reference_text = request.reference_text
    else:
        tone = models.ToneSettings(tone_name=request.tone_name, reference_text=request.reference_text)
        db.add(tone)
    db.commit()
    return {"status": "ok", "tone_name": tone.tone_name}

@app.get("/api/tones")
def get_tones(db: Session = Depends(get_db)) -> dict:
    tones = db.query(models.ToneSettings).all()
    return {tone.tone_name: tone.reference_text for tone in tones}

@app.post("/api/history/save")
def save_document_history(request: SaveDocumentRequest, db: Session = Depends(get_db)) -> dict:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_title = request.title if request.title else f"Documento_{timestamp}"
    filename = f"{doc_title.replace(' ', '_')}_{timestamp}.txt"
    file_path = os.path.join(VAULT_DIR, filename)
    
    # BUG FIX: Usando open() síncrono. Este endpoint es sync (def, no async def),
    # por lo que usar aiofiles con await era un RuntimeError garantizado.
    with open(file_path, mode="w", encoding="utf-8") as f:
        f.write(request.text)
        
    excerpt = request.text[:150] + "..." if len(request.text) > 150 else request.text
    
    db_doc = models.DocumentHistory(
        title=doc_title,
        file_path=file_path,
        excerpt=excerpt,
        tone_name=request.tone_name
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    return {"status": "ok", "doc_id": str(db_doc.id), "file_path": file_path}

@app.get("/api/history/list")
def list_document_history(db: Session = Depends(get_db)) -> list:
    docs = db.query(models.DocumentHistory).order_by(models.DocumentHistory.created_at.desc()).all()
    return [{
        "id": str(doc.id),  # Serialización explícita a str para consistencia con UUIDs
        "title": doc.title,
        "excerpt": doc.excerpt,
        "tone_name": doc.tone_name,
        "created_at": doc.created_at.isoformat()
    } for doc in docs]

@app.get("/api/history/read/{doc_id}")
def read_document_history(doc_id: str, db: Session = Depends(get_db)) -> dict:
    doc = db.query(models.DocumentHistory).filter(models.DocumentHistory.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
        
    # BUG FIX: Usando open() síncrono. Este endpoint es sync (def, no async def),
    # por lo que usar aiofiles con await era un RuntimeError garantizado.
    with open(doc.file_path, mode="r", encoding="utf-8") as f:
        content = f.read()
        
    return {"text": content}
