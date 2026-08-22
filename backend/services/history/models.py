from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List

class Base(DeclarativeBase):
    """Clase base de SQLAlchemy para herencia de metadatos ORM."""
    pass

class Chapter(Base):
    """
    Entidad que representa un capítulo o sección activa del manuscrito.
    Actúa como el 'Originator' en el patrón Memento.
    """
    __tablename__ = "chapters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relación uno-a-muchos: Un capítulo contiene múltiples instantáneas en su línea de tiempo
    snapshots: Mapped[List["Snapshot"]] = relationship(
        "Snapshot", back_populates="chapter", cascade="all, delete-orphan", order_by="Snapshot.version.desc()"
    )

class Snapshot(Base):
    """
    Representa el 'Memento'. Almacena el estado inmutable del texto 
    en un instante específico del flujo de dictado.
    """
    __tablename__ = "snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    chapter_id: Mapped[str] = mapped_column(String(36), ForeignKey("chapters.id"), nullable=False)
    content_json: Mapped[str] = mapped_column(Text, nullable=False)  # Árbol de nodos estructurado de Tiptap
    version: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    summary_of_changes: Mapped[str] = mapped_column(String(500), nullable=True)

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="snapshots")
