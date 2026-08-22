from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

class ToneName(str, Enum):
    SCI_FI = "Narrativa de Ciencia Ficción y Fantasía Épica"
    ROMANCE = "Romance Contemporáneo"
    THRILLER = "Misterio y Thriller"
    ACADEMIC = "No Ficción Académica"
    GENERAL = "General / Por Defecto"

class ProcessTextRequest(BaseModel):
    raw_text: str
    tone_name: str = "General / Por Defecto"
    format_type: str = "narrative"
    whisper_mode: bool = False
    context_buffer: list[str] = []

class ToneRequest(BaseModel):
    tone_name: ToneName
    reference_text: str

class SaveDocumentRequest(BaseModel):
    text: str
    tone_name: str = "General / Por Defecto"
    title: Optional[str] = None

class MetadataGenerationRequest(BaseModel):
    text: str = Field(..., min_length=50, description="Texto completo del manuscrito o capítulo.")
    tone_name: str = Field(..., description="Tono literario actual para guiar la clasificación.")

class BookMetadataResponse(BaseModel):
    synopsis: str = Field(..., description="Sinopsis comercial y atractiva orientada a contraportada.")
    target_audience: str = Field(..., description="Público objetivo demográfico y psicográfico estimado.")
    core_tropes: List[str] = Field(..., description="Lista de los tropos o clichés literarios dominantes detectados.")
    keywords: List[str] = Field(..., description="Palabras clave para indexación y SEO en tiendas digitales.")
    estimated_reading_time_minutes: int = Field(..., description="Tiempo estimado de lectura en minutos.")
    suggested_age_rating: str = Field(..., description="Clasificación por edades sugerida (ej. Middle Grade, YA, Adult).")
