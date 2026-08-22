import json
import wave
import logging

try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    raise ImportError('Vosk no está instalado. Ejecuta: pip install vosk')

logger = logging.getLogger("gema-worker")
_global_vosk_model = None

def _init_worker(model_path: str):
    """
    Initializer function for ProcessPoolExecutor.
    Loads the Vosk model once per worker process.
    """
    global _global_vosk_model
    try:
        _global_vosk_model = Model(model_path)
        logger.info(f"Worker initialized Vosk model from {model_path}")
    except Exception as e:
        logger.error(f"Worker failed to load Vosk model: {e}")

def sync_vosk_transcription(wav_path: str) -> str:
    """
    Synchronous Vosk transcription function. 
    Intended to be run in a separate process via ProcessPoolExecutor.
    """
    if not _global_vosk_model:
        raise RuntimeError("Vosk model not initialized in worker process.")

    with wave.open(wav_path, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("Invalid audio format for Vosk (must be 16kHz mono PCM)")

        rec = KaldiRecognizer(_global_vosk_model, wf.getframerate())
        rec.SetWords(True)

        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part_result = json.loads(rec.Result())
                text = part_result.get("text", "")
                if text:
                    results.append(text)

        part_result = json.loads(rec.FinalResult())
        results.append(part_result.get("text", ""))
        
        return " ".join(filter(None, results)).strip()
