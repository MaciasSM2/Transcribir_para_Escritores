"""
Gema — STT & Literary Assistant Backend
Punto de entrada principal. Solo inicialización, middleware y registro de routers.
Toda la lógica de negocio vive en backend/routers/.
"""
import logging

import models
from database import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.infrastructure.local_orchestrator import LocalEnvironmentOrchestrator
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import api_router

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("gema-backend")

# Inicializar tablas (Alembic gestiona migraciones; create_all es safety net para dev)
models.Base.metadata.create_all(bind=engine)

import os

orchestrator = LocalEnvironmentOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    strict_preflight = os.getenv("GEMA_STRICT_PREFLIGHT", "0").lower() in ("1", "true", "yes")
    await orchestrator.run_preflight_checks(strict=strict_preflight)
    yield
    # Lógica de apagado o liberación de buffers aquí si fuera necesario

app = FastAPI(title="Gema Local Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root() -> dict:
    return {"status": "ok", "message": "Gema STT Backend Running"}
