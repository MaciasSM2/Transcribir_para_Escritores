from typing import Protocol

class ILinguisticCleaner(Protocol):
    """
    Protocolo base que define el contrato inmutable para cualquier 
    módulo de limpieza de texto dentro del ecosistema Gema.
    """
    def clean(self, text: str) -> str:
        """
        Ejecuta la transformación y limpieza del texto provisto.
        
        Args:
            text (str): El fragmento de texto crudo o pre-procesado.
            
        Returns:
            str: Texto sanitizado según las reglas del módulo.
        """
        ...
