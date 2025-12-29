from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websockets import manager

router = APIRouter()

@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive. 
            # In a real app, we might process incoming messages too.
            data = await websocket.receive_text()
            # Echo for now or handle ping/pong
            # await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
