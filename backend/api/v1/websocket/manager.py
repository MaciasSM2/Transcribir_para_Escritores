from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    """
    Administra el ciclo de vida de las conexiones WebSocket activas.
    Implementa el patrón Singleton de facto para evitar fugas de hilos de red.
    """
    def __init__(self):
        # Almacena las conexiones activas indexadas por identificador de sesión
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """Acepta la conexión entrante del Host local y la registra en el pool."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remueve la conexión del pool de manera segura al cerrarse el canal."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_json_message(self, message: dict, client_id: str):
        """Envía un payload estructurado a un cliente específico (Single Cast)."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

# Instancia global inyectable del gestor de infraestructura
ws_manager = ConnectionManager()
