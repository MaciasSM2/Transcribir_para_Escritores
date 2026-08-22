from typing import Protocol

class AudioProcessor(Protocol):
    """Interfaz abstracta para la manipulación y limpieza de ondas de audio."""
    
    def sanitize_audio(self, input_path: str, output_path: str, whisper_mode: bool) -> None:
        """Acondiciona la señal de audio antes de ser enviada al motor ASR."""
        ...
