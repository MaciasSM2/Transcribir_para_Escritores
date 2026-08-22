# backend/services/nlp/dialogue_contracts.py
from pydantic import BaseModel, Field
from typing import List, Optional, Protocol

class DialogueLine(BaseModel):
    """Modelo de datos inmutable que representa una línea de diálogo segmentada."""
    character: str = Field(..., description="Nombre del personaje que habla o 'Narrador'.")
    speech: Optional[str] = Field(None, description="El texto explícito pronunciado por el personaje.")
    inciso: Optional[str] = Field(None, description="Acotación o acción del narrador intercalada.")
    is_action_only: bool = Field(False, description="True si el inciso describe una acción física sin verbo dicendi.")

class DialogueSceneResponse(BaseModel):
    """Payload estructurado de salida para el renderizado en el Lienzo Enriquecido."""
    formatted_prose: str = Field(..., description="Texto final maquetado listo para el folio A4.")
    lines: List[DialogueLine] = Field(..., description="Estructura desagregada para análisis de trama.")

class IDialogueDetector(Protocol):
    """Protocolo abstracto que define el contrato de inferencia para diálogos."""
    async def extract_dialogue_structure(self, raw_text: str) -> List[DialogueLine]:
        """Extrae la estructura semántica de una conversación a partir de texto plano."""
        ...
