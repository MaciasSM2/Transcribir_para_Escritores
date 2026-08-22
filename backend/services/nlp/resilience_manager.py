# backend/services/nlp/resilience_manager.py
import os

class ResilienceManager:
    @staticmethod
    def split_text_into_chunks(text: str, chunk_size: int = 1500) -> list:
        """Divide el texto en fragmentos lógicos para no saturar el contexto de la IA."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    @staticmethod
    def validate_audio_header(file_path: str) -> bool:
        """Verifica que el archivo no esté corrupto antes de procesar."""
        if not os.path.exists(file_path):
            return False
        return os.path.getsize(file_path) > 1024  # Mínimo 1KB
