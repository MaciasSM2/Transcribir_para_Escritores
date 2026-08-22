"""
conftest.py — Fixtures compartidas para toda la suite de tests de Gema.

Estrategia de BD:
  - Se usa SQLite en memoria (sqlite:///:memory:) para aislamiento total.
  - Cada test recibe una sesión limpia vía override de la dependency get_db.
  - Los modelos se crean desde Base.metadata, no desde Alembic, para velocidad.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar desde el directorio backend (conftest está en backend/tests/)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base
import models  # noqa: F401 — necesario para que Base.metadata incluya todas las tablas
from main import app

# ── BD en memoria ────────────────────────────────────────────────────────────
# StaticPool: reutiliza la MISMA conexión para todas las queries.
# Sin esto, SQLite en memoria crea una BD vacía por cada nueva conexión,
# lo que hace que create_all() y las queries subsecuentes vean BDs distintas.
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)



@pytest.fixture(scope="function")
def db_session():
    """Sesión de BD limpia por test. Crea y destruye las tablas en cada test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    TestClient con override de get_db → db_session en memoria.
    También bypasea get_current_user para no requerir token en tests unitarios.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return "test-user"

    from auth import get_current_user
    import database
    from api.v1.endpoints import audio, style, documents, tones

    # Override dependencies
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[audio.get_db] = override_get_db
    app.dependency_overrides[style.get_db] = override_get_db
    app.dependency_overrides[documents.get_db] = override_get_db
    app.dependency_overrides[tones.get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()



@pytest.fixture()
def sample_style_profile(db_session):
    """Inserta un StyleProfile de prueba en la BD de test."""
    import json
    profile = models.StyleProfile(
        tone_name="General / Por Defecto",
        style_display_name="General",
        reference_author="Autor de Prueba",
        avg_sentence_len=15,
        max_sentence_len=30,
        adjective_density=0.15,
        dialogue_ratio=0.2,
        short_sentence_ratio=0.3,
        ttr_target=0.6,
        flesch_target=60.0,
        forbidden_words=json.dumps([]),
        preferred_structures=json.dumps([]),
        compound_replacements=json.dumps({}),
    )
    db_session.add(profile)
    db_session.commit()
    return profile
