import uuid
from typing import List
from sqlalchemy.orm import Session
from .models import Snapshot, Chapter
from .repositories import IChapterRepository, ISnapshotRepository

class SnapshotOrchestrator:
    """
    Fachada de servicio encargada de coordinar los casos de uso del historial.
    Implementa el principio de Inversión de Dependencias (SOLID - D).
    """
    def __init__(self, session: Session, chapter_repo: IChapterRepository, snapshot_repo: ISnapshotRepository):
        self.session = session
        self.chapter_repo = chapter_repo
        self.snapshot_repo = snapshot_repo

    def create_checkpoint(self, chapter_id: str, content: str, change_description: str) -> Snapshot:
        """
        Captura el estado actual del lienzo y genera una nueva instantánea indexada en la línea de tiempo.
        Aplica el patrón Unit of Work a través de la gestión controlada de la sesión.
        """
        chapter = self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"El capítulo con ID {chapter_id} no existe en el registro local.")

        # Determinar el número de versión incremental continuo
        next_version = self.snapshot_repo.get_latest_version(chapter_id) + 1

        new_snapshot = Snapshot(
            id=str(uuid.uuid4()),
            chapter_id=chapter_id,
            content_json=content,
            version=next_version,
            summary_of_changes=change_description
        )

        try:
            self.snapshot_repo.save(new_snapshot)
            self.session.commit()  # Confirmación de la transacción atómica
            return new_snapshot
        except Exception as e:
            self.session.rollback()  # Reversión inmediata ante fallos físicos de disco
            raise RuntimeError(f"Fallo crítico al escribir el checkpoint en SQLite: {str(e)}")

    def rollback_to_snapshot(self, chapter_id: str, version: int) -> str:
        """
        Recupera un estado previo del manuscrito a partir de su índice de versión.
        Devuelve la cadena del payload listo para ser re-inyectado en el lienzo Tiptap.
        """
        history = self.snapshot_repo.get_history(chapter_id)
        target_snapshot = next((s for s in history if s.version == version), None)

        if not target_snapshot:
            raise KeyError(f"No se localizó la versión {version} para el capítulo seleccionado.")

        return target_snapshot.content_json
