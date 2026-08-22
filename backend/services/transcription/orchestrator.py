import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from .vosk_worker import _init_worker, sync_vosk_transcription

logger = logging.getLogger("gema-orchestrator")

class TranscriptionEngine:
    """Orquestador asíncrono para delegar inferencia a procesos aislados."""
    def __init__(self, model_path: str = "model_es"):
        self.executor = ProcessPoolExecutor(
            max_workers=2,
            initializer=_init_worker,
            initargs=(model_path,)
        )
        logger.info("TranscriptionEngine initialized with ProcessPoolExecutor")

    async def process_audio_file(self, wav_path: str) -> str:
        """Envía el archivo WAV purificado al ProcessPoolExecutor para transcribir."""
        loop = asyncio.get_running_loop()
        transcript = await loop.run_in_executor(self.executor, sync_vosk_transcription, wav_path)
        return transcript

    def shutdown(self):
        self.executor.shutdown(wait=True)
