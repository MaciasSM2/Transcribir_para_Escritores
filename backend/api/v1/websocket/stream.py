"""
WebSocket Endpoint — Streaming de Audio en Tiempo Real
Ruta: ws://localhost:8000/api/v1/stream/{client_id}

Recibe chunks binarios de audio PCM del frontend y los retransmite
al motor ASR (Vosk). El resultado se envía de vuelta como JSON:
  {"type": "partial", "text": "..."}   — resultado parcial
  {"type": "final",   "text": "..."}   — oración completa detectada
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.v1.websocket.manager import ws_manager

logger = logging.getLogger("gema-backend")
router = APIRouter()


@router.websocket("/stream/{client_id}")
async def websocket_stream_endpoint(websocket: WebSocket, client_id: str):
    """
    Canal binario bidireccional para streaming de dictado en tiempo real.
    El frontend envía Blob(arraybuffer) con PCM 16kHz mono.
    El backend responde con fragmentos de transcripción parcial/final.
    """
    await ws_manager.connect(client_id, websocket)
    logger.info(f"[WS] Cliente conectado: {client_id}")

    try:
        while True:
            # Recibimos chunk binario de audio del frontend
            chunk = await websocket.receive_bytes()

            # Placeholder: en producción, pasar chunk al motor Vosk/ASR aquí.
            # Por ahora confirmamos recepción para que el frontend no quede en limbo.
            await ws_manager.send_json_message(
                {"type": "ack", "bytes_received": len(chunk)},
                client_id
            )

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
        logger.info(f"[WS] Cliente desconectado limpiamente: {client_id}")
    except Exception as e:
        logger.error(f"[WS] Error inesperado en stream de {client_id}: {e}")
        ws_manager.disconnect(client_id)
