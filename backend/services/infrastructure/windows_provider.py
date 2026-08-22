# backend/services/infrastructure/windows_provider.py
import psutil
from typing import Dict, Any
from .system_guardian import IHardwareProvider

class Windows11HardwareProvider(IHardwareProvider):
    """
    Implementación concreta para la API de bajo nivel del sistema operativo Windows 11.
    Cumple con el principio de Sustitución de Liskov (SOLID - L).
    """
    
    def get_memory_metrics(self) -> Dict[str, Any]:
        """Extrae el estado del buffer de memoria RAM local."""
        virtual_mem = psutil.virtual_memory()
        return {
            "total_gb": round(virtual_mem.total / (1024 ** 3), 2),
            "available_gb": round(virtual_mem.available / (1024 ** 3), 2),
            "percent_used": virtual_mem.percent
        }

    def get_processor_metrics(self) -> Dict[str, Any]:
        """Captura los ciclos lógicos consumidos en el intervalo actual del kernel."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "logical_cores": psutil.cpu_count(logical=True)
        }
