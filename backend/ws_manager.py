"""WebSocket connection tracking for live message notifications."""

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # session_token -> WebSocket
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_token: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_token] = websocket

    def disconnect(self, session_token: str):
        self.active_connections.pop(session_token, None)

    async def send_to_user(self, session_token: str, message: dict):
        ws = self.active_connections.get(session_token)
        if ws is not None:
            await ws.send_json(message)
