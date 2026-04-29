import asyncio
from asyncio import AbstractEventLoop

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._loop: AbstractEventLoop | None = None

    def attach_loop(self, loop: AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast_json(self, payload: dict) -> None:
        stale_connections: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_json(payload)
            except Exception:  # noqa: BLE001
                stale_connections.append(connection)
        for connection in stale_connections:
            self.disconnect(connection)

    def emit(self, payload: dict) -> None:
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast_json(payload), self._loop)

    @property
    def connection_count(self) -> int:
        return len(self._connections)


connection_manager = ConnectionManager()
