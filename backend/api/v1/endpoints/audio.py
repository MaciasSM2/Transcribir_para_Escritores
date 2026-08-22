"""
Router: Transcripción de audio
Endpoints:
  POST /api/transcribe/file    — recibe audio, encola worker, responde 202
  GET  /api/transcribe/status/{job_id} — polling del estado del job
"""
import os
import shutil
import uuid
import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import models
from database import SessionLocal, get_db
import schemas
from services.audio.ffmpeg_processor import FFmpegAudioProcessor
from services.transcription.orchestrator import TranscriptionEngine
from services.nlp.refinement_pipeline import LinguisticRefinementPipeline
from services.nlp.resilience_manager import ResilienceManager

logger = logging.getLogger("gema-backend")

router = APIRouter(tags=["transcription"])

# Ruta de modelo unificada — debe coincidir con local_orchestrator.py
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "model_es")

# Inicialización de servicios
audio_processor = FFmpegAudioProcessor()
transcription_engine = TranscriptionEngine(VOSK_MODEL_PATH)
refinement_pipeline = LinguisticRefinementPipeline()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)


# get_db importado desde database.py — no duplicar aquí


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
    whisper_mode: bool = False,
    tone_name: str = "General / Por Defecto",
    format_type: str = "narrative"
) -> None:
    db = SessionLocal()
    try:
        job = db.query(models.JobHistory).filter(models.JobHistory.id == job_id).first()
        if not job:
            logger.error(f"[BG] Job {job_id} no encontrado en BD. Abortando worker.")
            return
        logger.info(f"[BG] Iniciando procesamiento para job {job_id} ({job.filename})")
        
        # 1. Filtro Espectral Avanzado / Modo Susurro
        audio_processor.sanitize_audio(temp_input_path, temp_wav_path, whisper_mode)
        
        # 2. Transcripción ASR Offline
        raw_transcription = await transcription_engine.process_audio_file(temp_wav_path)
        
        # 3. Pipeline NLP Semántico
        final_prose = await refinement_pipeline.refine_transcription(raw_transcription, tone_name)

        job.transcription = final_prose
        job.status = "completed"
        db.commit()
        logger.info(f"[BG] Job {job_id} completado y persistido.")

    except Exception as e:
        logger.error(f"[BG] Fallo en job {job_id}: {e}")
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
        for path in [temp_input_path, temp_wav_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as e:
                    logger.error(f"[BG] Fuga de disco en job {job_id}: {path} — {e}")


# ---------------------------------------------------------------------------
# ENDPOINT DE TRANSCRIPCIÓN (Patrón Async Request-Reply)
# ---------------------------------------------------------------------------
@router.post("/upload", status_code=202)
async def transcribe_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    whisper_mode: bool = Form(False),
    tone_name: str = Form("General / Por Defecto"),
    format_type: str = Form("narrative"),
    db: Session = Depends(get_db),
) -> dict:
    # Validación estricta temprana
    if not file.content_type or not file.content_type.startswith("audio/"):
        logger.warning(f"MIME inválido o ausente: {file.filename} ({file.content_type})")
        raise HTTPException(status_code=400, detail="El tipo MIME no corresponde a un audio.")

    allowed_extensions = {".mp3", ".wav", ".ogg", ".opus", ".m4a", ".webm", ".aac", ".flac"}
    raw_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    file_ext = "".join(c for c in raw_ext if c.isalnum() or c == ".").lower()
    if not file_ext or file_ext not in allowed_extensions:
        logger.warning(f"Extensión no permitida o vacía: '{file_ext}' en '{file.filename}'")
        raise HTTPException(status_code=400, detail="Extensión de archivo no permitida.")

    unique_id = str(uuid.uuid4())
    temp_input_path = os.path.join(TEMP_DIR, f"temp_{unique_id}{file_ext}")
    temp_wav_path = os.path.join(TEMP_DIR, f"temp_{unique_id}_converted.wav")

    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.close()

    db_job = models.JobHistory(
        filename=file.filename,
        original_format=file_ext.lstrip("."),
        status="pending",
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    logger.info(f"Job {db_job.id} encolado para '{file.filename}' — respondiendo 202.")

    background_tasks.add_task(
        process_audio_background,
        job_id=db_job.id,
        temp_input_path=temp_input_path,
        temp_wav_path=temp_wav_path,
        whisper_mode=whisper_mode,
        tone_name=tone_name,
        format_type=format_type,
    )

    return {
        "message": "Audio recibido y procesando en segundo plano.",
        "job_id": db_job.id,
        "status": "pending",
    }


# ---------------------------------------------------------------------------
# ENDPOINT DE POLLING
# ---------------------------------------------------------------------------
@router.get("/status/{job_id}")
def get_transcription_status(job_id: str, db: Session = Depends(get_db)) -> dict:
    job = db.query(models.JobHistory).filter(models.JobHistory.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")
    return {
        "job_id": job.id,
        "status": job.status,
        "transcription": job.transcription,
    }

@router.get("/jobs")
def get_jobs_history(db: Session = Depends(get_db)) -> list:
    """Historial de jobs de transcripción (más reciente primero)."""
    jobs = db.query(models.JobHistory).order_by(models.JobHistory.created_at.desc()).all()
    return [
        {
            "id":            str(job.id),
            "filename":      job.filename,
            "transcription": job.transcription,
            "createdAt":     job.created_at.isoformat(),
        }
        for job in jobs
    ]

# ---------------------------------------------------------------------------
# ENDPOINT DE PROCESAMIENTO LARGO
# ---------------------------------------------------------------------------
@router.post("/process-large-text")
async def process_large_text(request: schemas.ProcessTextRequest):
    # 1. Fragmentación para Resiliencia
    chunks = ResilienceManager.split_text_into_chunks(request.raw_text)
    processed_chunks = []
    
    # 2. Procesamiento secuencial (protege la memoria)
    for chunk in chunks:
        # El semáforo en ollama_adapter asegura que no se sature el hardware
        refined = await refinement_pipeline.refine_transcription(chunk, request.tone_name)
        processed_chunks.append(refined)
        
    return {"text": "\n\n".join(processed_chunks)}
