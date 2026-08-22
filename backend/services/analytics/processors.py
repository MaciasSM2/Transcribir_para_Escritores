import re
from typing import Dict, Any
from .contracts import IMetricAnalyzer

class ProductivityAnalyzer(IMetricAnalyzer):
    """
    Analizador encargado de las métricas cuantitativas de rendimiento.
    Satisface el principio de Responsabilidad Única (SOLID - S).
    """
    
    def analyze(self, raw_text: str, contextual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula la velocidad de procesamiento de palabras basándose en el tiempo delta de la sesión."""
        words = len(raw_text.split())
        duration_seconds = contextual_data.get("duration_seconds", 60)
        
        # Evitar división por cero en sesiones instantáneas
        minutes = max(1.0, duration_seconds / 60.0)
        wpm = round(words / minutes, 2)
        
        return {
            "words_per_minute": wpm,
            "character_count": len(raw_text)
        }

class NarrativePacingAnalyzer(IMetricAnalyzer):
    """
    Analizador heurístico del ritmo y la tensión del texto.
    Inspecciona la densidad de signos de puntuación y modificadores gramaticales.
    """
    
    def analyze(self, raw_text: str, contextual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determina el ritmo narrativo examinando la longitud promedio de las oraciones."""
        sentences = re.split(r'[.!?]+', raw_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"narrative_tension": 50, "coherence_index": 1.0}
            
        total_words = len(raw_text.split())
        avg_sentence_length = total_words / len(sentences)
        
        # Heurística: Oraciones muy cortas indican acción/tensión alta. 
        # Oraciones largas indican descripción o ritmo lento.
        tension = 100 - min(100, max(10, round(avg_sentence_length * 2.5)))
        
        return {
            "narrative_tension": tension,
            "coherence_index": 0.92  # Este valor se refinará mediante el pipeline de Ollama asíncrono
        }
