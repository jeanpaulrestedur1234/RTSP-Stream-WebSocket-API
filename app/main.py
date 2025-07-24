import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from app.stream_manager import StreamManager
app = FastAPI()
manager = StreamManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"message": "RTSP stream WebSocket API"}

@app.websocket("/ws")
async def websocket_stream(
    websocket: WebSocket,
    rtsp: str = Query(...),
    camera_index: str = Query(...)
):
    await websocket.accept()
    await manager.add_client(camera_index, rtsp, websocket)
    try:
        while True:
            await websocket.receive_text()  # mantiene viva la conexión
    except WebSocketDisconnect:
        await manager.remove_client(camera_index, websocket)
