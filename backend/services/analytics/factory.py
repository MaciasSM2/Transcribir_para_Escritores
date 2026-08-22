from typing import List
from .contracts import IMetricAnalyzer
from .processors import ProductivityAnalyzer, NarrativePacingAnalyzer

class MetricAnalyzerFactory:
    """Garantiza la creación limpia y centralizada de analizadores (Factory Pattern)."""
    
    @staticmethod
    def get_registered_analyzers() -> List[IMetricAnalyzer]:
        """Devuelve las instancias de los analizadores registrados en el ecosistema."""
        return [
            ProductivityAnalyzer(),
            NarrativePacingAnalyzer()
        ]
