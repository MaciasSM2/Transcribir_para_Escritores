from fastapi import APIRouter
from api.v1.endpoints import audio, style, documents, tones, auth, metadata, dna, system, dialogue, export, history
from api.v1.websocket.stream import router as ws_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(audio.router, prefix="/audio")
api_router.include_router(style.router, prefix="/style")
api_router.include_router(documents.router, prefix="/docs")
api_router.include_router(tones.router, prefix="/tones")
api_router.include_router(metadata.router, prefix="/metadata", tags=["Análisis de Metadatos"])
api_router.include_router(dna.router, prefix="/dna", tags=["ADN Literario"])
api_router.include_router(system.router, prefix="/system", tags=["Métricas del Sistema"])
api_router.include_router(dialogue.router, prefix="/dialogue", tags=["Procesamiento de Diálogos"])
api_router.include_router(export.router, prefix="/export", tags=["Exportación Documental"])
api_router.include_router(history.router, prefix="/history", tags=["Historial de Cambios"])
api_router.include_router(ws_router)  # WebSocket sin prefijo adicional: /api/v1/stream/{client_id}
