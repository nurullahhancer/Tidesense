from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import safe_decode_token
from app.websocket.manager import connection_manager

router = APIRouter()


@router.websocket("/ws/live")
async def live_websocket(websocket: WebSocket, token: str = Query(...)) -> None:
    payload = safe_decode_token(token)
    if payload is None:
        await websocket.close(code=1008)
        return

    user_id = payload.get("id")
    await connection_manager.connect(websocket, user_id=user_id)
    await connection_manager.broadcast_presence()
    await websocket.send_json(
        {
            "type": "connection",
            "payload": {
                "message": "WebSocket connection established",
                "username": payload.get("sub"),
                "role": payload.get("role"),
            },
        }
    )
    try:
        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_json({"type": "pong", "payload": {}})
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id=user_id)
        await connection_manager.broadcast_presence()
