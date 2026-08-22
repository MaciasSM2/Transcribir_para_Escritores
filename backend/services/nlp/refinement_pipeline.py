import logging
from .lexical_cleaner import LexicalCleaner
from .semantic_refiner import SemanticRefiner

logger = logging.getLogger("gema-pipeline")

class LinguisticRefinementPipeline:
    """
    Orquestador central que implementa el patrón Facade para unificar
    los filtros mecánicos y heurísticos en una única llamada limpia.
    """

    def __init__(self):
        self.lexical_stage = LexicalCleaner()
        self.semantic_stage = SemanticRefiner()

    async def refine_transcription(self, raw_speech_text: str, tone_name: str) -> str:
        """
        Procesa el dictado a través de la cadena de limpieza total.
        
        Args:
            raw_speech_text (str): El texto crudo e incoherente que sale del motor ASR.
            tone_name (str): El perfil de estilo/tono seleccionado.
            
        Returns:
            str: Prosa pulida, estructurada y lista para el lienzo de escritura.
        """
        logger.info("Iniciando pipeline de refinamiento lingüístico...")
        
        # PASO 1: Sanitización mecánica ultrarrápida (Complejidad O(n))
        # Elimina muletillas físicas y balbuceos iniciales, aliviando la carga de la IA.
        sanitized_lexical = self.lexical_stage.clean(raw_speech_text)
        
        # PASO 2: Reestructuración semántica profunda mediante LLM Local
        # Se encarga de disolver marcadores conversacionales complejos ("pues", "bueno")
        refined_prose = await self.semantic_stage.clean_deep(sanitized_lexical, tone_name)
        
        logger.info("Pipeline de refinamiento completado con éxito.")
        return refined_prose
