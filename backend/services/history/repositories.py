from typing import Protocol, List, Optional
from sqlalchemy.orm import Session
from .models import Chapter, Snapshot

class IChapterRepository(Protocol):
    """Protocolo abstracto que define el contrato inmutable para la gestión de capítulos (SOLID - I)."""
    def get_by_id(self, chapter_id: str) -> Optional[Chapter]: ...
    def save(self, chapter: Chapter) -> None: ...

class ISnapshotRepository(Protocol):
    """Protocolo que rige la persistencia de las instantáneas del control de versiones."""
    def get_latest_version(self, chapter_id: str) -> int: ...
    def save(self, snapshot: Snapshot) -> None: ...
    def get_history(self, chapter_id: str) -> List[Snapshot]: ...

class SQLAlchemyChapterRepository(IChapterRepository):
    """Implementación concreta utilizando sesiones activas de SQLAlchemy."""
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, chapter_id: str) -> Optional[Chapter]:
        return self.session.query(Chapter).filter(Chapter.id == chapter_id).first()

    def save(self, chapter: Chapter) -> None:
        self.session.add(chapter)
        # Nota: El commit se delega al orquestador (Unit of Work)

class SQLAlchemySnapshotRepository(ISnapshotRepository):
    """Manejo de operaciones de persistencia relacional para objetos Snapshot."""
    def __init__(self, session: Session):
        self.session = session

    def get_latest_version(self, chapter_id: str) -> int:
        result = self.session.query(Snapshot.version)\
            .filter(Snapshot.chapter_id == chapter_id)\
            .order_by(Snapshot.version.desc()).first()
        return result[0] if result else 0

    def save(self, snapshot: Snapshot) -> None:
        self.session.add(snapshot)

    def get_history(self, chapter_id: str) -> List[Snapshot]:
        return self.session.query(Snapshot).filter(Snapshot.chapter_id == chapter_id).order_by(Snapshot.version.desc()).all()
