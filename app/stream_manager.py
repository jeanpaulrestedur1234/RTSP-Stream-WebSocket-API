from app.camera_stream import CameraStream

class StreamManager:
    def __init__(self):
        self.streams = {}

    async def add_client(self, camera_index, rtsp_url, websocket):
        if camera_index not in self.streams:
            self.streams[camera_index] = CameraStream(rtsp_url)
        await self.streams[camera_index].add_client(websocket)

    async def remove_client(self, camera_index, websocket):
        if camera_index in self.streams:
            await self.streams[camera_index].remove_client(websocket)
            if not self.streams[camera_index].clients:
                del self.streams[camera_index]
