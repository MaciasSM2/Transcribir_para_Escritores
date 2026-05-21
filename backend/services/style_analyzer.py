"""
StyleAnalyzer — Capas 1 y 2 del Motor Estilométrico Zero-IA.

CAPA 1 — MORFOLÓGICA (spaCy):
  Tokenización, POS tagging, extracción de lemas, tiempo verbal dominante,
  detección de patrones compuestos ADV+ADJ, secuencias POS top-3.

CAPA 2 — ESTADÍSTICA (textstat + pyphen + pySBD):
  Segmentación de frases (respeta abreviaturas), métricas de legibilidad,
  conteo silábico, desviación estándar de longitud de frases, TTR,
  densidad de adjetivos y cálculo de alignment_score vs. StyleProfile.
"""

from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

import pyphen
import pysbd
import spacy
import textstat

logger = logging.getLogger("gema-analyzer")

# ---------------------------------------------------------------------------
# Inicialización de herramientas (una sola vez al importar el módulo)
# ---------------------------------------------------------------------------

_nlp: Optional[spacy.language.Language] = None
_dic_es = pyphen.Pyphen(lang="es")
_segmenter = pysbd.Segmenter(language="es", clean=False)

def _get_nlp() -> Optional[spacy.language.Language]:
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("es_core_news_sm")
            logger.info("StyleAnalyzer: modelo spaCy cargado.")
        except OSError:
            logger.error("StyleAnalyzer: es_core_news_sm no encontrado.")
    return _nlp


# ---------------------------------------------------------------------------
# Dataclass de resultados
# ---------------------------------------------------------------------------

@dataclass
class StyleMetrics:
    # --- Métricas de ritmo ---
    sentence_count: int = 0
    avg_sentence_len: float = 0.0       # palabras/frase media
    max_sentence_len: int = 0           # frase más larga (palabras)
    sentence_len_stddev: float = 0.0    # desviación estándar (monotonía)
    short_sentence_ratio: float = 0.0   # % frases < 10 palabras

    # --- Riqueza léxica ---
    word_count: int = 0
    unique_words: int = 0
    ttr: float = 0.0                    # Type/Token Ratio

    # --- Densidad morfológica ---
    adjective_density: float = 0.0      # adj / sustantivos (0-1+)
    adverb_count: int = 0               # total adverbios (para alerta -mente)
    mente_adverb_count: int = 0         # adverbios terminados en -mente

    # --- Legibilidad ---
    flesch_score: float = 0.0
    fernandez_huerta: float = 0.0

    # --- Ritmo silábico ---
    avg_syllables_per_word: float = 0.0

    # --- Análisis morfológico ---
    dominant_verb_tense: str = "desconocido"  # "pasado" | "presente" | "mixto"
    pos_sequences_top3: list = field(default_factory=list)  # ["VERB+NOUN", ...]
    compound_patterns: list = field(default_factory=list)   # ["muy grande", ...]

    # --- Score de alineamiento (0-100) ---
    alignment_score: float = 0.0

    # --- Referencia del perfil (para el gráfico de radar) ---
    profile_data: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Clase principal
# ---------------------------------------------------------------------------

class StyleAnalyzer:
    """
    Analiza un texto y devuelve StyleMetrics.
    No modifica el texto — solo mide.
    """

    def analyze(self, text: str, style_profile: Optional[dict] = None) -> StyleMetrics:
        """
        Punto de entrada principal.
        style_profile: dict con campos de StyleProfile (ya cargado desde DB).
        Si es None, alignment_score y profile_data quedan en 0/{}.
        """
        if not text or not text.strip():
            return StyleMetrics()

        metrics = StyleMetrics()
        nlp = _get_nlp()

        # ── CAPA 1: MORFOLÓGICA ──────────────────────────────────────────────
        if nlp:
            doc = nlp(text)
            self._capa1_morfologica(doc, metrics)

        # ── CAPA 2A: ESTADÍSTICA DE FRASES (pySBD) ──────────────────────────
        sentences = _segmenter.segment(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        self._capa2a_ritmo(sentences, metrics)

        # ── CAPA 2B: LEGIBILIDAD (textstat) ─────────────────────────────────
        self._capa2b_legibilidad(text, metrics)

        # ── CAPA 2C: SÍLABAS (pyphen) ────────────────────────────────────────
        self._capa2c_silabas(text, metrics)

        # ── ALINEAMIENTO VS. PERFIL ──────────────────────────────────────────
        if style_profile:
            metrics.alignment_score = self._calcular_alignment(metrics, style_profile)
            metrics.profile_data = {
                "avg_sentence_len": style_profile.get("avg_sentence_len", 0),
                "max_sentence_len": style_profile.get("max_sentence_len", 0),
                "ttr_target": style_profile.get("ttr_target", 0),
                "adjective_density": style_profile.get("adjective_density", 0),
                "flesch_target": style_profile.get("flesch_target", 0),
                "reference_author": style_profile.get("reference_author", ""),
                "style_display_name": style_profile.get("style_display_name", ""),
            }

        return metrics

    # ── IMPLEMENTACIÓN DE CAPAS ──────────────────────────────────────────────

    def _capa1_morfologica(self, doc, metrics: StyleMetrics) -> None:
        """Capa 1: POS tagging, lemas, tiempos verbales, patrones ADV+ADJ."""
        tokens_validos = [t for t in doc if not t.is_punct and not t.is_space]

        metrics.word_count = len(tokens_validos)
        metrics.unique_words = len({t.lemma_.lower() for t in tokens_validos})
        metrics.ttr = round(metrics.unique_words / metrics.word_count, 3) if metrics.word_count else 0.0

        # Conteo POS
        pos_counts: Counter = Counter(t.pos_ for t in tokens_validos)
        noun_count = pos_counts.get("NOUN", 0) + pos_counts.get("PROPN", 0)
        adj_count = pos_counts.get("ADJ", 0)
        metrics.adverb_count = pos_counts.get("ADV", 0)
        metrics.adjective_density = round(adj_count / noun_count, 3) if noun_count else 0.0

        # Adverbios en -mente
        metrics.mente_adverb_count = sum(
            1 for t in tokens_validos if t.pos_ == "ADV" and t.text.lower().endswith("mente")
        )

        # Tiempo verbal dominante
        verb_tenses: list[str] = []
        for token in doc:
            if token.pos_ == "VERB":
                morph = token.morph.get("Tense")
                if morph:
                    verb_tenses.extend(morph)

        if verb_tenses:
            tense_counter = Counter(verb_tenses)
            dominant = tense_counter.most_common(1)[0][0]
            total = sum(tense_counter.values())
            pres = tense_counter.get("Pres", 0)
            past = tense_counter.get("Past", 0)
            if abs(pres - past) / total < 0.2:
                metrics.dominant_verb_tense = "mixto"
            elif dominant == "Pres":
                metrics.dominant_verb_tense = "presente"
            else:
                metrics.dominant_verb_tense = "pasado"

        # Secuencias POS top-3 (bigramas de POS)
        pos_seq = [t.pos_ for t in tokens_validos]
        bigrams = [f"{pos_seq[i]}+{pos_seq[i+1]}" for i in range(len(pos_seq) - 1)]
        metrics.pos_sequences_top3 = [seq for seq, _ in Counter(bigrams).most_common(3)]

        # Patrones compuestos ADV+ADJ ("muy grande", "bastante raro")
        compounds: list[str] = []
        for i in range(len(doc) - 1):
            t1, t2 = doc[i], doc[i + 1]
            if t1.pos_ == "ADV" and t2.pos_ == "ADJ":
                compounds.append(f"{t1.text.lower()} {t2.text.lower()}")
        metrics.compound_patterns = compounds

    def _capa2a_ritmo(self, sentences: list[str], metrics: StyleMetrics) -> None:
        """Capa 2A: estadística de longitud de frases."""
        if not sentences:
            return

        lengths = [len(s.split()) for s in sentences]
        metrics.sentence_count = len(sentences)
        metrics.avg_sentence_len = round(sum(lengths) / len(lengths), 1)
        metrics.max_sentence_len = max(lengths)
        metrics.short_sentence_ratio = round(
            sum(1 for l in lengths if l < 10) / len(lengths), 3
        )

        # Desviación estándar (mide monotonía de ritmo)
        if len(lengths) > 1:
            mean = metrics.avg_sentence_len
            variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
            metrics.sentence_len_stddev = round(math.sqrt(variance), 2)

    def _capa2b_legibilidad(self, text: str, metrics: StyleMetrics) -> None:
        """Capa 2B: índices Flesch y Fernández-Huerta vía textstat."""
        textstat.set_lang("es")
        try:
            metrics.flesch_score = round(textstat.flesch_reading_ease(text), 1)
            # Fernández-Huerta: variante española del índice Flesch
            metrics.fernandez_huerta = round(textstat.fernandez_huerta(text), 1)
        except Exception as e:
            logger.warning(f"textstat error: {e}")

    def _capa2c_silabas(self, text: str, metrics: StyleMetrics) -> None:
        """Capa 2C: sílabas promedio por palabra usando pyphen."""
        words = re.findall(r'\b[a-záéíóúüñ]+\b', text.lower())
        if not words:
            return
        total_syllables = sum(
            max(1, len(_dic_es.inserted(w).split("-")))
            for w in words
        )
        metrics.avg_syllables_per_word = round(total_syllables / len(words), 2)

    def _calcular_alignment(self, metrics: StyleMetrics, profile: dict) -> float:
        """
        Calcula un score 0-100 que mide qué tan cerca está el texto
        del perfil estilístico del tono seleccionado.
        Cada dimensión aporta hasta 20 puntos (5 dimensiones = 100).
        """
        score = 0.0

        def puntuar_ratio(valor_usuario, valor_target, tolerancia=0.3) -> float:
            """Devuelve 0-20 según qué tan cerca está valor_usuario de valor_target."""
            if valor_target == 0:
                return 10.0
            desviacion = abs(valor_usuario - valor_target) / valor_target
            return max(0.0, 20.0 * (1 - desviacion / tolerancia))

        # 1. Ritmo (avg_sentence_len)
        score += puntuar_ratio(
            metrics.avg_sentence_len,
            profile.get("avg_sentence_len", metrics.avg_sentence_len),
            tolerancia=0.5
        )

        # 2. Riqueza léxica (TTR)
        score += puntuar_ratio(
            metrics.ttr,
            profile.get("ttr_target", metrics.ttr),
            tolerancia=0.4
        )

        # 3. Densidad de adjetivos
        score += puntuar_ratio(
            metrics.adjective_density,
            profile.get("adjective_density", metrics.adjective_density),
            tolerancia=0.5
        )

        # 4. Legibilidad (Flesch)
        score += puntuar_ratio(
            metrics.flesch_score,
            profile.get("flesch_target", metrics.flesch_score),
            tolerancia=0.4
        )

        # 5. Proporción de frases cortas
        score += puntuar_ratio(
            metrics.short_sentence_ratio,
            profile.get("short_sentence_ratio", metrics.short_sentence_ratio),
            tolerancia=0.5
        )

        return round(min(100.0, score), 1)
