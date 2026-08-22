# backend/services/infrastructure/local_orchestrator.py
import shutil
import os
import logging
import httpx
from .interfaces import ISystemValidator

logger = logging.getLogger("gema-local-orchestrator")

class LocalEnvironmentOrchestrator(ISystemValidator):
    """
    Orquestador encargado de certificar la soberanía y disponibilidad del entorno local.
    Aplica el patrón Facade para centralizar los diagnósticos pre-vuelo del sistema.
    """

    def __init__(self, ollama_url: str = "http://localhost:11434", vosk_model_path: str = "model_es"):
        self.ollama_url = f"{ollama_url}/api/tags"
        if not os.path.isabs(vosk_model_path):
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            vosk_model_path = os.path.join(backend_dir, vosk_model_path)
        self.vosk_model_path = vosk_model_path

    def verify_software_dependency(self, binary_name: str) -> bool:
        """
        Verifica la presencia de herramientas CLI esenciales en el sistema operativo host.
        
        Args:
            binary_name (str): Nombre del ejecutable a buscar (ej. 'ffmpeg').
            
        Returns:
            bool: True si el componente está mapeado en las variables de entorno.
        """
        binary_path = shutil.which(binary_name)
        if binary_path:
            logger.info(f"Componente del sistema localizado con éxito: {binary_name} en {binary_path}")
            return True
        logger.error(f"Falta dependencia crítica del sistema: {binary_name} no se encuentra en el PATH.")
        return False

    async def verify_service_availability(self) -> bool:
        """
        Ejecuta un sondeo de salud hacia el demonio local de Ollama.
        
        Returns:
            bool: True si el servidor de inferencia local responde.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ollama_url, timeout=3.0)
                if response.status_code == 200:
                    logger.info("Conexión con el servidor de inferencia local Ollama establecida con éxito.")
                    return True
                return False
        except (httpx.ConnectError, httpx.TimeoutException):
            logger.error("No se pudo conectar con Ollama. Asegúrate de ejecutar 'ollama serve' localmente.")
            return False

    def verify_vosk_model_integrity(self) -> bool:
        """
        Verifica la existencia del modelo del lenguaje para el motor ASR sin conexión a red.
        
        Returns:
            bool: True si la carpeta del modelo de Vosk está presente en la raíz y no vacía.
        """
        if os.path.exists(self.vosk_model_path) and os.path.isdir(self.vosk_model_path):
            if len(os.listdir(self.vosk_model_path)) > 0:
                logger.info(f"Modelo acústico offline verificado en la ruta: ./{self.vosk_model_path}")
                return True
        logger.error(f"Modelo de transcripción offline no localizado o vacío. Falta la carpeta: ./{self.vosk_model_path}")
        return False

    async def run_preflight_checks(self, strict: bool = False) -> dict:
        """
        Ejecuta la suite completa de diagnósticos pre-vuelo de la infraestructura local.
        Si strict=True, lanza una excepción de sistema si alguna validación falla.
        Si strict=False, registra el estado de los subsistemas y permite degradación elegante.
        """
        logger.info("Iniciando auditoría preventiva de entorno 100% Local...")
        
        has_ffmpeg = self.verify_software_dependency("ffmpeg")
        has_vosk = self.verify_vosk_model_integrity()
        has_ollama = await self.verify_service_availability()
        
        status = {
            "ffmpeg": has_ffmpeg,
            "vosk_model": has_vosk,
            "ollama": has_ollama,
        }
        
        if strict:
            if not has_ffmpeg:
                raise RuntimeError("Falta FFmpeg. El procesamiento espectral de audio no estará disponible.")
            if not has_vosk:
                raise RuntimeError("Falta el modelo acústico de Vosk. La transcripción offline fallará.")
            if not has_ollama:
                raise RuntimeError("El demonio de Ollama no responde en el puerto 11434.")
        
        logger.info(f"Auditoría de entorno local finalizada: {status}")
        return status
