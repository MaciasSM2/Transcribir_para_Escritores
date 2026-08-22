import subprocess
import logging
import os
from .interfaces import AudioProcessor

logger = logging.getLogger("gema-audio-processor")

class FFmpegAudioProcessor(AudioProcessor):
    """Procesador de audio de alta fidelidad basado en grafos de filtros de FFmpeg."""

    def __init__(self):
        # Filtro de paso alto para mitigar ruidos graves de la calle (motores, viento)
        self.highpass_freq: int = 150
        # Filtro de paso bajo para atenuar siseos electrónicos agudos
        self.lowpass_freq: int = 3600

    def sanitize_audio(self, input_path: str, output_path: str, whisper_mode: bool) -> None:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Archivo de entrada no localizado: {input_path}")

        # Construcción del grafo de filtros de audio (-af)
        # afftdn: Reducción de ruido en el dominio de la frecuencia mediante FFT
        filters = f"highpass=f={self.highpass_freq},lowpass=f={self.lowpass_freq},afftdn=nf=-22:om=o"

        if whisper_mode:
            # speechnorm: Aplica compresión expansiva dinámica en tiempo real.
            # Eleva susurros lejanos e iguala la ganancia sin saturar la señal.
            filters += ",speechnorm=e=12:r=0.0005:l=1"
        else:
            # Normalización estándar para dictados controlados
            filters += ",loudnorm=I=-16:TP=-1.5:LRA=11"

        command = [
            'ffmpeg', '-y', '-i', input_path,
            '-af', filters,
            '-ar', '16000', '-ac', '1', output_path
        ]

        logger.info(f"Ejecutando acondicionamiento acústico. Modo Susurro: {whisper_mode}")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Fallo en la tubería de FFmpeg: {result.stderr}")
            raise RuntimeError(f"FFmpeg pipeline error: {result.stderr.strip()}")
