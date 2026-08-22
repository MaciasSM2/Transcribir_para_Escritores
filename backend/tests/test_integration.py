import pytest
import shutil
from services.audio.ffmpeg_processor import FFmpegAudioProcessor
from services.nlp.ollama_adapter import OllamaCoherenceAdapter

@pytest.mark.asyncio
async def test_ollama_connection():
    adapter = OllamaCoherenceAdapter(model_name="llama3")
    raw = "Hola... mmm, esto es un ehh test."
    result = await adapter.refine_prose(raw, "General")
    # Verificamos que siempre retorne un texto válido (inferido si Ollama está activo o fallback original si está offline)
    assert len(result) > 0
    if adapter.is_available():
        assert "ehh" not in result.lower()
    else:
        assert result == raw

def test_ffmpeg_processor_existence():
    processor = FFmpegAudioProcessor()
    # Verificamos que el binario de FFmpeg sea accesible
    assert shutil.which("ffmpeg") is not None
