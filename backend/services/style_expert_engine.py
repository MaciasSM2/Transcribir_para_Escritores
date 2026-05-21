"""
FakeAIRulesEngine — Motor Experto Zero-IA (Capas 3 y 4).

CAPA 3 — SEMÁNTICA (LiteraryThesaurus + compound_replacements):
  - Tesauro POS-aware: para cada token VERB/ADJ/NOUN busca su lema en
    literary_thesaurus del tono activo. Solo sustituye si POS coincide.
  - compound_replacements: detecta patrones ADV+ADJ desde StyleProfile
    y reemplaza la frase compuesta completa ("muy grande" → "imponente").
  - Reconstruye corrected_text respetando el contrato con CorrectionReviewer.

CAPA 4 — ESTRUCTURAL (StyleProfile + métricas):
  - Alerta "rhythm":     frases > max_sentence_len del perfil.
  - Alerta "monotonía":  σ de longitud de frases > umbral interno.
  - Alerta "vicio_mente": adverbios -mente > 3 en el texto.
  - Alerta "queísmo":    patrón "que ... que" repetido en la misma frase.
  - Alerta "forbidden":  palabras del campo forbidden_words del perfil.
  - Alerta "structure":  preferred_structures no detectadas en el texto.
"""

from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass, field
from typing import Optional

import spacy
import pysbd

from .style_analyzer import StyleAnalyzer, StyleMetrics

logger = logging.getLogger("gema-engine")

# ── Inicialización lazy del modelo spaCy (reutiliza el del StyleAnalyzer) ──

_nlp: Optional[spacy.language.Language] = None
_segmenter = pysbd.Segmenter(language="es", clean=False)


def _get_nlp() -> Optional[spacy.language.Language]:
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("es_core_news_sm")
        except OSError:
            logger.error("FakeAIRulesEngine: es_core_news_sm no encontrado.")
    return _nlp


# ────────────────────────────────────────────────────────────────────────────
# Dataclasses de respuesta
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class Suggestion:
    """Un cambio léxico propuesto por el motor."""
    type: str          # "replacement" | "compound_replacement"
    original: str      # "caminó"
    replacement: str   # "acechó"
    pos: str           # "VERB"
    intensity: str     # "poético"
    context: str       # "acción"


@dataclass
class StyleAlert:
    """Alerta estructural generada por Capa 4."""
    type: str          # "rhythm" | "forbidden" | "vicio_mente" | "queísmo" | "structure" | "monotonía"
    severity: str      # "info" | "warning" | "critical"
    message: str
    sentence_index: Optional[int] = None  # índice (0-based) de la frase infractora


@dataclass
class EngineResponse:
    """Respuesta completa del motor — backward-compatible con CorrectionReviewer."""
    corrected_text: str
    suggestions: list = field(default_factory=list)   # List[Suggestion]
    style_report: dict = field(default_factory=dict)  # StyleMetrics serializada + profile
    alerts: list = field(default_factory=list)        # List[StyleAlert]


# ────────────────────────────────────────────────────────────────────────────
# Motor principal
# ────────────────────────────────────────────────────────────────────────────

class FakeAIRulesEngine:
    """
    Motor experto de corrección estilística Zero-IA.
    No usa LLMs. Todo es determinista: DB + reglas + spaCy.
    """

    def __init__(self):
        self._style_analyzer = StyleAnalyzer()

    # ── Punto de entrada público ────────────────────────────────────────────

    def analyze_and_fix(
        self,
        text: str,
        tone_name: str,
        style_profile: Optional[dict],
        thesaurus_entries: list[dict],
        prohibited_words: list[dict],
    ) -> EngineResponse:
        """
        Procesa el texto completo y devuelve un EngineResponse.

        Args:
            text:             texto crudo del escritor
            tone_name:        nombre del tono (ej. "Misterio y Thriller")
            style_profile:    dict con los campos de StyleProfile (puede ser None)
            thesaurus_entries: lista de dicts de LiteraryThesaurus para el tono
            prohibited_words: lista de dicts de ProhibitedWord para el tono
        """
        if not text or not text.strip():
            return EngineResponse(corrected_text=text)

        # ── Capas 1 y 2: análisis estilométrico ─────────────────────────────
        metrics: StyleMetrics = self._style_analyzer.analyze(text, style_profile)

        # ── Capa 3: sustituciones semánticas ────────────────────────────────
        corrected_text, suggestions = self._capa3_semantica(
            text, thesaurus_entries, style_profile
        )

        # ── Capa 4: alertas estructurales ───────────────────────────────────
        alerts = self._capa4_estructural(text, metrics, style_profile, prohibited_words)

        # ── Serializar style_report ──────────────────────────────────────────
        style_report = self._serialize_metrics(metrics)

        return EngineResponse(
            corrected_text=corrected_text,
            suggestions=suggestions,
            style_report=style_report,
            alerts=alerts,
        )

    # ────────────────────────────────────────────────────────────────────────
    # CAPA 3 — SEMÁNTICA
    # ────────────────────────────────────────────────────────────────────────

    def _capa3_semantica(
        self,
        text: str,
        thesaurus_entries: list[dict],
        style_profile: Optional[dict],
    ) -> tuple[str, list[Suggestion]]:
        """
        Aplica sustituciones léxicas en dos pasos:
          1. compound_replacements (ADV+ADJ) — sobre el texto plano.
          2. Tesauro POS-aware — via spaCy sobre el texto resultante.
        """
        suggestions: list[Suggestion] = []
        working_text = text

        # ── Paso 1: compound_replacements (ADV+ADJ) ──────────────────────────
        if style_profile:
            compound_json = style_profile.get("compound_replacements", "{}")
            try:
                compounds: dict[str, str] = (
                    json.loads(compound_json) if isinstance(compound_json, str) else compound_json
                )
            except (json.JSONDecodeError, TypeError):
                compounds = {}

            for pattern, replacement in sorted(compounds.items(), key=lambda x: -len(x[0])):
                # Regex case-insensitive, límites de palabra para no romper compuestos mayores
                regex = re.compile(re.escape(pattern), re.IGNORECASE)
                if regex.search(working_text):
                    working_text = regex.sub(replacement, working_text)
                    suggestions.append(Suggestion(
                        type="compound_replacement",
                        original=pattern,
                        replacement=replacement,
                        pos="ADV+ADJ",
                        intensity="poético",
                        context="descripción",
                    ))

        # ── Paso 2: Tesauro POS-aware ─────────────────────────────────────────
        nlp = _get_nlp()
        if not nlp or not thesaurus_entries:
            return working_text, suggestions

        # Construir índice: (lemma_lower, pos) → entrada de mayor prioridad
        thesaurus_index: dict[tuple[str, str], dict] = {}
        for entry in thesaurus_entries:
            key = (entry["source_lemma"].lower(), entry["pos_tag"])
            existing = thesaurus_index.get(key)
            if not existing or entry.get("priority", 0) > existing.get("priority", 0):
                thesaurus_index[key] = entry

        doc = nlp(working_text)
        # Construimos el texto de atrás hacia delante para que los offsets no se desplacen
        replacements_by_char: list[tuple[int, int, str, Suggestion]] = []

        for token in doc:
            if token.pos_ not in ("VERB", "ADJ", "NOUN"):
                continue
            key = (token.lemma_.lower(), token.pos_)
            entry = thesaurus_index.get(key)
            if not entry:
                continue

            original_form = token.text
            target = entry["target_word"]

            # Preservar capitalización de la primera letra si el token la tiene
            if original_form and original_form[0].isupper() and target:
                target = target[0].upper() + target[1:]

            replacements_by_char.append((
                token.idx,
                token.idx + len(token.text),
                target,
                Suggestion(
                    type="replacement",
                    original=original_form,
                    replacement=target,
                    pos=token.pos_,
                    intensity=entry.get("intensity", "neutro"),
                    context=entry.get("context_hint", ""),
                ),
            ))

        # Aplicar sustituciones de derecha a izquierda (offsets estables)
        result_chars = list(working_text)
        seen_original: set[str] = set()  # evitar duplicar la misma sugerencia

        for start, end, replacement, suggestion in sorted(replacements_by_char, key=lambda x: -x[0]):
            result_chars[start:end] = list(replacement)
            if suggestion.original.lower() not in seen_original:
                seen_original.add(suggestion.original.lower())
                suggestions.append(suggestion)

        final_text = "".join(result_chars)
        return final_text, suggestions

    # ────────────────────────────────────────────────────────────────────────
    # CAPA 4 — ESTRUCTURAL (alertas)
    # ────────────────────────────────────────────────────────────────────────

    def _capa4_estructural(
        self,
        text: str,
        metrics: StyleMetrics,
        style_profile: Optional[dict],
        prohibited_words: list[dict],
    ) -> list[StyleAlert]:
        """Genera alertas estructurales basadas en métricas y perfil del tono."""
        alerts: list[StyleAlert] = []
        sentences = [s.strip() for s in _segmenter.segment(text) if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]

        # ── 4.1 Alerta "rhythm": frases demasiado largas ─────────────────────
        max_len = style_profile.get("max_sentence_len", 30) if style_profile else 30
        for i, (sentence, length) in enumerate(zip(sentences, sentence_lengths)):
            if length > max_len:
                alerts.append(StyleAlert(
                    type="rhythm",
                    severity="warning" if length < max_len * 1.5 else "critical",
                    message=(
                        f"Frase de {length} palabras supera el límite de {max_len} "
                        f"del perfil. Considera dividirla en dos."
                    ),
                    sentence_index=i,
                ))

        # ── 4.2 Alerta "monotonía": σ baja en longitud de frases ─────────────
        MONOTONIA_UMBRAL = 3.5  # σ mínima para variación rítmica saludable
        if metrics.sentence_len_stddev < MONOTONIA_UMBRAL and metrics.sentence_count >= 3:
            alerts.append(StyleAlert(
                type="monotonía",
                severity="info",
                message=(
                    f"Ritmo monótono: desviación estándar de longitud de frases es "
                    f"{metrics.sentence_len_stddev:.1f} (ideal > {MONOTONIA_UMBRAL}). "
                    "Varía la longitud de las frases para añadir cadencia."
                ),
            ))

        # ── 4.3 Alerta "vicio_mente": adverbios -mente excesivos ─────────────
        MENTE_UMBRAL = 3
        if metrics.mente_adverb_count > MENTE_UMBRAL:
            alerts.append(StyleAlert(
                type="vicio_mente",
                severity="warning",
                message=(
                    f"Se detectaron {metrics.mente_adverb_count} adverbios terminados en "
                    f"-mente. Más de {MENTE_UMBRAL} por fragmento debilita el estilo. "
                    "Sustituye por verbos de acción o adjetivos precisos."
                ),
            ))

        # ── 4.4 Alerta "queísmo": "que" repetido en la misma frase ───────────
        queismo_pattern = re.compile(r'\bque\b.{0,60}\bque\b', re.IGNORECASE)
        for i, sentence in enumerate(sentences):
            if queismo_pattern.search(sentence):
                alerts.append(StyleAlert(
                    type="queísmo",
                    severity="info",
                    message=(
                        "Patrón 'que...que' detectado. Considera restructurar la frase "
                        "para evitar la repetición del nexo."
                    ),
                    sentence_index=i,
                ))

        # ── 4.5 Alerta "forbidden": palabras del perfil ───────────────────────
        # Combina forbidden_words del StyleProfile + tabla prohibited_words
        forbidden_from_profile: list[str] = []
        if style_profile:
            fw_json = style_profile.get("forbidden_words", "[]")
            try:
                forbidden_from_profile = json.loads(fw_json) if isinstance(fw_json, str) else fw_json
            except (json.JSONDecodeError, TypeError):
                forbidden_from_profile = []

        # Palabras de la tabla ProhibitedWord (ya filtradas por tone_name en main.py)
        forbidden_from_table = [pw["word"] for pw in prohibited_words]
        all_forbidden = set(w.lower() for w in forbidden_from_profile + forbidden_from_table)

        # Buscar en cada frase
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            for word in all_forbidden:
                # Búsqueda de palabra completa
                if re.search(r'\b' + re.escape(word) + r'\b', sentence_lower):
                    # Obtener sugerencia si viene de la tabla
                    suggestion_hint = ""
                    for pw in prohibited_words:
                        if pw["word"].lower() == word:
                            suggestion_hint = f" Sugerencia: «{pw['suggestion']}»."
                            break
                    alerts.append(StyleAlert(
                        type="forbidden",
                        severity="warning",
                        message=(
                            f"La palabra «{word}» rompe la atmósfera del tono activo.{suggestion_hint}"
                        ),
                        sentence_index=i,
                    ))

        # ── 4.6 Alerta "structure": patrones POS preferidos no encontrados ────
        if style_profile:
            ps_json = style_profile.get("preferred_structures", "[]")
            try:
                preferred: list[str] = json.loads(ps_json) if isinstance(ps_json, str) else ps_json
            except (json.JSONDecodeError, TypeError):
                preferred = []

            if preferred:
                detected = set(metrics.pos_sequences_top3)
                missing = [p for p in preferred if p not in detected]
                if missing:
                    alerts.append(StyleAlert(
                        type="structure",
                        severity="info",
                        message=(
                            f"Patrones POS característicos del tono no detectados: "
                            f"{', '.join(missing)}. Tu texto podría carecer de la "
                            "estructura sintáctica del estilo seleccionado."
                        ),
                    ))

        return alerts

    # ────────────────────────────────────────────────────────────────────────
    # Serialización
    # ────────────────────────────────────────────────────────────────────────

    def _serialize_metrics(self, metrics: StyleMetrics) -> dict:
        """Convierte StyleMetrics a dict JSON-serializable para la respuesta HTTP."""
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
