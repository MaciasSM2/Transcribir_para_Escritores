from typing import Protocol, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class MetricPayload(BaseModel):
    """Encapsula los resultados agregados del análisis de una sesión de escritura."""
    chapter_id: str = Field(..., description="Identificador único del capítulo evaluado.")
    words_per_minute: float = Field(..., description="Velocidad media de dictado/escritura.")
    narrative_tension: int = Field(..., description="Escala de tensión dramática estimada (1-100).")
    coherence_index: float = Field(..., description="Coeficiente de consistencia semántica local.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Momento del cálculo.")

class IMetricAnalyzer(Protocol):
    """Contrato abstracto para las estrategias de análisis analítico (SOLID - I)."""
    def analyze(self, raw_text: str, contextual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el escaneo algorítmico sobre la prosa provista."""
        ...
