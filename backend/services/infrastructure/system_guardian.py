# backend/services/infrastructure/system_guardian.py
import psutil
import logging
from typing import Protocol, Dict, Any

logger = logging.getLogger("gema-system-guardian")

class IHardwareProvider(Protocol):
    """Contrato formal para la extracción de métricas de rendimiento del Host local."""
    def get_memory_metrics(self) -> Dict[str, Any]: ...
    def get_processor_metrics(self) -> Dict[str, Any]: ...

class SystemGuardian:
    """
    Orquestador encargado de mitigar escenarios Out-Of-Memory (OOM) en el entorno local.
    Aplica el principio de Responsabilidad Única (SOLID - S) para vigilar la salud del hardware.
    """
    def __init__(self, provider: IHardwareProvider):
        self._provider = provider
        # Límites de seguridad operativa local
        self.RAM_THRESHOLD_PERCENT = 95.0

    def inspect_environment_safety(self) -> Dict[str, Any]:
        """
        Inspecciona el estado térmico y de carga de la máquina de desarrollo.
        
        Returns:
            Dict[str, Any]: Diagnóstico de salud con bandera de bloqueo preventivo.
        """
        mem_stats = self._provider.get_memory_metrics()
        cpu_stats = self._provider.get_processor_metrics()
        
        # Estrategia de prevención contra cuellos de botella locales
        is_unsafe = mem_stats["percent_used"] > self.RAM_THRESHOLD_PERCENT
        
        if is_unsafe:
            logger.warning(
                f"Alerta de saturación de recursos locales: RAM al {mem_stats['percent_used']}%."
                " Activando estrangulamiento preventivo de hilos de inferencia."
            )
            
        return {
            "healthy": not is_unsafe,
            "ram_usage_percent": mem_stats["percent_used"],
            "cpu_usage_percent": cpu_stats["cpu_percent"],
            "action_required": "THROTTLE_INFERENCE" if is_unsafe else "NONE"
        }
