# backend/services/nlp/interfaces.py
from typing import Protocol, List

class IMetadataProvider(Protocol):
    """Protocolo abstracto para proveedores de análisis semántico avanzado."""
    
    async def extract_semantic_features(self, text: str, tone_context: str) -> dict:
        """Analiza el texto y extrae características de alto nivel como sinopsis y tropos."""
        ...
