"""
Router: Motor Estilométrico
Endpoints:
  POST /api/process-text    — corrige texto según perfil de tono
  POST /api/analyze-text    — devuelve métricas puras sin modificar el texto
  GET  /api/engine/status   — estado del motor y perfiles cargados
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from auth import get_current_user
from database import SessionLocal, get_db
from nlp_processor import StyleProcessorLegacy
from schemas import ProcessTextRequest
from services.style_analyzer import StyleAnalyzer
from services.style_expert_engine import FakeAIRulesEngine
from services.nlp.base_cleaner import TextCleaner
from services.nlp.ollama_adapter import OllamaCoherenceAdapter
from services.nlp.narrative_analyzer import NarrativeAnalyzer

logger = logging.getLogger("gema-backend")

router = APIRouter(tags=["style"])

# Servicios (singleton por proceso)
style_processor_legacy = StyleProcessorLegacy()
fake_ai_engine = FakeAIRulesEngine()
style_analyzer = StyleAnalyzer()
text_cleaner = TextCleaner()
ollama_adapter = OllamaCoherenceAdapter(model_name="llama3")
narrative_analyzer = NarrativeAnalyzer(model="llama3")


@router.post("/process-text")
async def process_text(request: ProcessTextRequest, db: Session = Depends(get_db)) -> dict:
    """
    Pipeline de 3 capas + Análisis de Tensión:
      1. TextCleaner     — elimina muletillas (regex, ~0ms)
      2. OllamaService   — coherencia narrativa y análisis de tensión
      3. FakeAIRulesEngine — aplica ADN literario determinista
    """
    # ── Capa 1: Limpieza de muletillas (regex, instantánea) ─────────────────
    cleaned_text = text_cleaner.clean_disfluencies(request.raw_text)
    logger.info(f"[process-text] Capa 1 completada. Chars: {len(request.raw_text)} → {len(cleaned_text)}")

    # ── Obtener perfil de tono (necesario para Capas 2 y 3) ─────────────────
    profile_row = db.query(models.StyleProfile).filter(
        models.StyleProfile.tone_name == request.tone_name
    ).first()

    # ── Capa 2: Coherencia con Ollama (LLM local, fallback si no disponible) y Análisis de Tensión ─
    tone_desc = profile_row.style_display_name if profile_row else str(request.tone_name)
    
    import asyncio
    coherent_text, tension_report = await asyncio.gather(
        ollama_adapter.refine_prose(cleaned_text, tone_desc, request.format_type, request.context_buffer),
        narrative_analyzer.analyze_tension(cleaned_text)
    )
    
    logger.info(f"[process-text] Capa 2 completada. Chars: {len(cleaned_text)} → {len(coherent_text)}")

    # ── Capa 3: Motor experto determinista ───────────────────────────────────
    if not profile_row:
        logger.info(f"[process-text] Sin StyleProfile para '{request.tone_name}' — usando fallback legacy.")
        tone_settings = db.query(models.ToneSettings).filter(
            models.ToneSettings.tone_name == request.tone_name
        ).first()
        reference_text = tone_settings.reference_text if tone_settings else ""
        corrected_text = style_processor_legacy.process_text(
            coherent_text, request.tone_name, reference_text
        )
        return {"corrected_text": corrected_text, "suggestions": [], "alerts": [], "style_report": {}, "tension_data": tension_report}

    profile_dict = {
        "avg_sentence_len":      profile_row.avg_sentence_len,
        "max_sentence_len":      profile_row.max_sentence_len,
        "ttr_target":            profile_row.ttr_target,
        "adjective_density":     profile_row.adjective_density,
        "flesch_target":         profile_row.flesch_target,
        "short_sentence_ratio":  profile_row.short_sentence_ratio,
        "reference_author":      profile_row.reference_author,
        "style_display_name":    profile_row.style_display_name,
        "forbidden_words":       profile_row.forbidden_words,
        "preferred_structures":  profile_row.preferred_structures,
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

    result = fake_ai_engine.analyze_and_fix(
        text=coherent_text,
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
        "tension_data":   tension_report,
    }


@router.post("/analyze-text")
def analyze_text(request: ProcessTextRequest, db: Session = Depends(get_db)) -> dict:
    """Devuelve métricas estilométricas puras sin modificar el texto."""
    profile_row = db.query(models.StyleProfile).filter(
        models.StyleProfile.tone_name == request.tone_name
    ).first()

    profile_dict = None
    if profile_row:
        profile_dict = {
            "avg_sentence_len":     profile_row.avg_sentence_len,
            "max_sentence_len":     profile_row.max_sentence_len,
            "ttr_target":           profile_row.ttr_target,
            "adjective_density":    profile_row.adjective_density,
            "flesch_target":        profile_row.flesch_target,
            "short_sentence_ratio": profile_row.short_sentence_ratio,
            "reference_author":     profile_row.reference_author,
            "style_display_name":   profile_row.style_display_name,
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


@router.get("/engine/status")
def engine_status(db: Session = Depends(get_db)) -> dict:
    """Estado del motor: versión, tonos, tesauro y disponibilidad de Ollama."""
    profiles = db.query(models.StyleProfile).all()
    thesaurus_count = db.query(models.LiteraryThesaurus).count()
    prohibited_count = db.query(models.ProhibitedWord).count()
    dna_count = db.query(models.LiteraryDNA).count()

    return {
        "engine_version": "3.0-pipeline",
        "engine_mode": "cleaner+ollama+expert-rules",
        "pipeline": [
            {"layer": 1, "name": "TextCleaner",      "type": "regex",      "status": "active"},
            {"layer": 2, "name": "OllamaCoherenceAdapter", "type": "llm-local",  "status": "active" if ollama_adapter.is_available() else "offline"},
            {"layer": 3, "name": "FakeAIRulesEngine","type": "expert-rules","status": "active"},
        ],
        "ollama_model": ollama_adapter.model_name,
        "profiles_loaded": [
            {
                "tone_name":        p.tone_name,
                "display_name":     p.style_display_name,
                "reference_author": p.reference_author,
            }
            for p in profiles
        ],
        "thesaurus_entries":    thesaurus_count,
        "prohibited_words":     prohibited_count,
        "literary_dna_records": dna_count,
    }
