"""
Real-time queue status over WebSocket. The homepage monitor connects here
instead of polling /queue/status on a timer -- the server pushes an update
every couple of seconds over one persistent connection instead of the
client repeatedly asking.
"""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services import queue_service as svc

router = APIRouter()


@router.websocket("/ws/queue")
async def ws_queue_status(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(svc.current_queue_snapshot())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
