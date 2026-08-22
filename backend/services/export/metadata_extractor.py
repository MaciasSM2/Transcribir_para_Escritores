import re
from typing import List
from .contracts import IMetadataExtractor, ManuscriptMetadata

class ManuscriptMetadataExtractor(IMetadataExtractor):
    """
    Componente encargado de auditar la estructura cuantitativa del texto.
    Aplica heurísticas rápidas en memoria para no saturar el hilo del servidor.
    """

    def __init__(self):
        # Expresión regular para identificar nombres propios potencialmente candidatos a personajes
        self._entity_pattern = re.compile(r'\b[A-Z][a-z\u00e0-\u00fc]+\b')

    def _extract_unique_entities(self, text: str) -> List[str]:
        """Identifica de manera heurística los nombres propios dentro del flujo textual."""
        # Filtramos palabras comunes al inicio de las oraciones que simulan nombres propios
        exclusions = {"El", "La", "Los", "Las", "Un", "Una", "Prólogo", "Capítulo"}
        found = self._entity_pattern.findall(text)
        unique_entities = {name for name in found if name not in exclusions}
        return sorted(list(unique_entities))

    def extract_metrics(self, raw_text: str) -> ManuscriptMetadata:
        if not raw_text.strip():
            return ManuscriptMetadata(word_count=0, character_count=0, estimated_pages=0, detected_entities=[])

        words = raw_text.split()
        word_count = len(words)
        char_count = len(raw_text)
        
        # Heurística editorial estándar: ~250 palabras por página en un layout A4 convencional
        estimated_pages = max(1, round(word_count / 250))
        detected_entities = self._extract_unique_entities(raw_text)

        return ManuscriptMetadata(
            word_count=word_count,
            character_count=char_count,
            estimated_pages=estimated_pages,
            detected_entities=detected_entities
        )
