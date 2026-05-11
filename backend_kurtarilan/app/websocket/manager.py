import asyncio
from asyncio import AbstractEventLoop

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._user_connections: dict[int, set[WebSocket]] = {}
        self._loop: AbstractEventLoop | None = None

    def attach_loop(self, loop: AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, websocket: WebSocket, user_id: int | None = None) -> None:
        await websocket.accept()
        self._connections.add(websocket)
        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int | None = None) -> None:
        self._connections.discard(websocket)
        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

    async def broadcast_json(self, payload: dict) -> None:
        stale_connections: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_json(payload)
            except Exception:  # noqa: BLE001
                stale_connections.append(connection)

        # Stale connection handling (cleanup from both sets)
        for connection in stale_connections:
            self._connections.discard(connection)
            # Cleanup from user mapping
            for uid, conn_set in list(self._user_connections.items()):
                if connection in conn_set:
                    conn_set.discard(connection)
                    if not conn_set:
                        del self._user_connections[uid]

    async def broadcast_presence(self) -> None:
        await self.broadcast_json(
            {
                "type": "presence",
                "payload": {
                    "active_user_ids": self.active_user_ids,
                    "active_count": len(self._user_connections),
                    "connection_count": self.connection_count,
                },
            }
        )

    def emit(self, payload: dict) -> None:
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast_json(payload), self._loop)

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    @property
    def active_user_ids(self) -> list[int]:
        return sorted(self._user_connections.keys())


connection_manager = ConnectionManager()
