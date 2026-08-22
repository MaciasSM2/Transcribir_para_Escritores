# backend/services/infrastructure/interfaces.py
from typing import Protocol

class ISystemValidator(Protocol):
    """Contrato formal para la validación de dependencias críticas de hardware y software local."""
    
    def verify_software_dependency(self, binary_name: str) -> bool:
        """Verifica si un binario del sistema está accesible en el PATH del sistema operativo."""
        ...

    async def verify_service_availability(self) -> bool:
        """Verifica si los demonios locales (Ollama API) responden correctamente."""
        ...
