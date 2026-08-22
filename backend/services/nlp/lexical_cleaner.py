import re
from .base_refiner import ILinguisticCleaner

class LexicalCleaner(ILinguisticCleaner):
    """
    Filtro determinista encargado de la remoción de ruidos acústicos explícitos,
    tartamudeos y anomalías mecánicas de capitalización.
    """

    def __init__(self, custom_dictionary: dict = None):
        # Patrón para identificar muletillas fonéticas y vacilaciones comunes
        self.fillers_pattern = re.compile(
            r'\b(eh|em|mmm|eee|estee?|ah|uhm|o sea|bueno|pues)\b', 
            re.IGNORECASE
        )
        # Patrón para detectar palabras duplicadas consecutivas (balbuceos / vacilaciones)
        self.stutter_pattern = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE)
        # Diccionario de reemplazo: { "lo que escuchó": "lo que debe ser" }
        self.custom_dictionary = custom_dictionary or {
            "a el bar": "Aethelgard",
            "mago de oz": "Mago de Os",
            "ser de luz": "Zerdelyus"
        }

    def _apply_custom_vocabulary(self, text: str) -> str:
        """Sustituye errores fonéticos comunes por los nombres reales de la obra."""
        for faulty, correct in self.custom_dictionary.items():
            pattern = re.compile(rf'\b{re.escape(faulty)}\b', re.IGNORECASE)
            text = pattern.sub(correct, text)
        return text

    def _fix_mid_sentence_capitalization(self, text: str) -> str:
        """Corrige mayúsculas erráticas generadas por pausas en el dictado automático."""
        # Divide el texto por oraciones para respetar las mayúsculas legítimas tras un punto
        sentences = text.split('. ')
        fixed_sentences = []

        for sentence in sentences:
            if not sentence:
                continue
            # Mantiene la primera letra intacta y procesa el resto de la oración
            first_char = sentence[0]
            rest_of_sentence = sentence[1:]
            
            # Reemplaza mayúsculas que no van después de un punto por minúsculas
            # Evita alterar siglas o nombres propios mediante una heurística simple de espaciado
            rest_of_sentence = re.sub(
                r'\s([A-Z])([a-z])', 
                lambda m: f" {m.group(1).lower()}{m.group(2)}", 
                rest_of_sentence
            )
            fixed_sentences.append(first_char + rest_of_sentence)

        return '. '.join(fixed_sentences)

    def clean(self, text: str) -> str:
        if not text.strip():
            return ""

        # 1. Aplicar vocabulario del autor primero
        cleaned = self._apply_custom_vocabulary(text)

        # 2. Eliminar muletillas fonéticas explícitas
        cleaned = self.fillers_pattern.sub("", cleaned)
        
        # 3. Corregir tartamudeos y duplicaciones de habla
        cleaned = self.stutter_pattern.sub(r"\1", cleaned)
        
        # 3. Normalizar mayúsculas erráticas en mitad de las oraciones
        cleaned = self._fix_mid_sentence_capitalization(cleaned)
        
        # 4. Colapsar espacios en blanco duplicados residuales
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
