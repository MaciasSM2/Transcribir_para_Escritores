from typing import Protocol, List
from pydantic import BaseModel, Field

class ManuscriptMetadata(BaseModel):
    """Esquema de datos inmutable para las métricas analíticas de la obra."""
    word_count: int = Field(..., description="Cantidad total de palabras procesadas.")
    character_count: int = Field(..., description="Total de caracteres con espacios.")
    estimated_pages: int = Field(..., description="Cálculo estimado de páginas en formato A4 estándar.")
    detected_entities: List[str] = Field(default_factory=list, description="Lista de personajes o locaciones identificadas.")

class IMetadataExtractor(Protocol):
    """Contrato abstracto para componentes encargados de la minería de texto literario."""
    def extract_metrics(self, raw_text: str) -> ManuscriptMetadata:
        """Analiza el texto para extraer métricas y entidades."""
        ...

class IDocumentExporter(Protocol):
    """Contrato para las estrategias de renderizado y exportación binaria."""
    def generate_file(self, raw_text: str) -> bytes:
        """Construye el archivo binario listo para transmisión HTTP."""
        ...
