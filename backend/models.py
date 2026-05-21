from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from database import Base
import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class JobHistory(Base):
    __tablename__ = "job_history"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    filename = Column(String, index=True)
    original_format = Column(String)
    transcription = Column(Text, nullable=True)  # Nulo hasta que el worker complete
    status = Column(String, default="pending")   # "pending" | "completed" | "error"
    # Usando datetime.UTC (aware) en lugar de utcnow() que está deprecated desde Python 3.12
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

class ToneSettings(Base):
    __tablename__ = "tone_settings"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    tone_name = Column(String, unique=True, index=True)
    reference_text = Column(Text)

class DocumentHistory(Base):
    __tablename__ = "document_history"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    title = Column(String, index=True)
    file_path = Column(String)
    excerpt = Column(Text)
    tone_name = Column(String)
    # Usando datetime.UTC (aware) en lugar de utcnow() que está deprecated desde Python 3.12
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))


# ---------------------------------------------------------------------------
# MOTOR ESTILOMÉTRICO — Tablas del Sistema Experto Literario
# ---------------------------------------------------------------------------

class LiteraryDNA(Base):
    """
    Huella digital de autores reales, medida de corpus.
    Fuente canónica de los perfiles estilísticos.
    Los campos JSON (preferred_patterns) se almacenan como Text y se
    parsean con json.loads() en el código.
    """
    __tablename__ = "literary_dna"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    author_name  = Column(String, nullable=False, index=True)   # "Raymond Chandler"
    genre        = Column(String, nullable=False)                # "Noir"
    tone_name    = Column(String, nullable=False, index=True)    # FK lógica a style_profiles

    # Métricas estilométricas medidas del corpus del autor
    avg_sentence_length = Column(Float)   # palabras/frase
    adjective_ratio     = Column(Float)   # adj / sustantivos
    lexical_richness    = Column(Float)   # TTR: palabras_únicas / total
    dialogue_ratio      = Column(Float)   # proporción de texto en diálogo

    # Patrones POS más frecuentes — JSON string: ["PRON+VERB+ADV", "SUST+VERB"]
    preferred_patterns = Column(Text)


class StyleProfile(Base):
    """
    Parámetros operativos por tono, derivados del LiteraryDNA.
    El motor los consulta en tiempo real para calcular alertas y umbrales.
    """
    __tablename__ = "style_profiles"

    tone_name          = Column(String, primary_key=True)   # "Misterio y Thriller"
    style_display_name = Column(String)                     # "Novela Negra / Hardboiled"
    reference_author   = Column(String)                     # "Raymond Chandler"

    # Umbrales de ritmo
    avg_sentence_len = Column(Integer)   # palabras/frase objetivo
    max_sentence_len = Column(Integer)   # umbral para alerta "rhythm"

    # Umbrales estadísticos
    adjective_density    = Column(Float)  # adj/sustantivo objetivo
    dialogue_ratio       = Column(Float)  # % texto en diálogo objetivo
    short_sentence_ratio = Column(Float)  # % frases < 10 palabras
    ttr_target           = Column(Float)  # Type/Token Ratio objetivo
    flesch_target        = Column(Float)  # Puntuación Flesch objetivo

    # Listas de control — JSON strings
    forbidden_words       = Column(Text)  # ["etéreo", "divino", "maravilloso"]
    preferred_structures  = Column(Text)  # ["PRON+VERB+ADV", "SUST+VERB"]
    compound_replacements = Column(Text)  # {"muy grande": "imponente"}


class LiteraryThesaurus(Base):
    """
    Tesauro literario POS-aware.
    Las búsquedas se hacen por LEMA (forma base), no por forma flexionada,
    para que "caminó", "camina" y "caminaba" encuentren la misma entrada.
    """
    __tablename__ = "literary_thesaurus"

    id           = Column(String, primary_key=True, default=generate_uuid)
    tone_name    = Column(String, nullable=False, index=True)  # FK lógica a style_profiles
    source_lemma = Column(String, nullable=False, index=True)  # "caminar" (no "caminó")
    target_word  = Column(String, nullable=False)               # "acechar"
    pos_tag      = Column(String, nullable=False)               # "VERB" / "ADJ" / "NOUN"
    intensity    = Column(String)                               # "vulgar" / "neutro" / "poético" / "técnico"
    context_hint = Column(String)                               # "diálogo" / "descripción" / "acción"
    priority     = Column(Integer, default=5)                   # 1-10, mayor = se aplica primero


class ProhibitedWord(Base):
    """
    Palabras que rompen la atmósfera de un tono específico.
    A diferencia del campo forbidden_words del StyleProfile (lista corta),
    esta tabla permite razones y sugerencias contextuales por palabra.
    """
    __tablename__ = "prohibited_words"

    id         = Column(String, primary_key=True, default=generate_uuid)
    tone_name  = Column(String, nullable=False, index=True)
    word       = Column(String, nullable=False, index=True)
    reason     = Column(String)     # "Tono positivo/coloquial"
    suggestion = Column(String)     # "inquietante"
