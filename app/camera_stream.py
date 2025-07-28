import av
import asyncio
import numpy as np
import cv2

class CameraStream:
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.clients = {}  # websocket -> task
        self.running = False
        self.latest_frame = None
        self.frame_lock = asyncio.Lock()
        self._task = None

    async def start(self):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._relay_loop())
        print(f"🎥 Cámara iniciada: {self.rtsp_url}")

    async def _relay_loop(self):
        try:
            container = av.open(self.rtsp_url, options={"rtsp_transport": "tcp"})
            stream = container.streams.video[0]
            stream.thread_type = "AUTO"

            frame_count = 0
            last_time = asyncio.get_event_loop().time()

            for packet in container.demux(stream):
                if not self.running:
                    break

                for frame in packet.decode():
                    if not self.running:
                        break

                    img = frame.to_ndarray(format="bgr24")
                    img = cv2.resize(img, (640, 360))
                    success, jpeg = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                    if not success:
                        continue

                    jpeg_bytes = jpeg.tobytes()

                    async with self.frame_lock:
                        self.latest_frame = jpeg_bytes

                    frame_count += 1
                    now = asyncio.get_event_loop().time()
                    if now - last_time >= 1:
                        print(f"📦 {self.rtsp_url} FPS enviados: {frame_count}")
                        frame_count = 0
                        last_time = now

                    await asyncio.sleep(1 / 30)

        except Exception as e:
            print(f"❌ Error en la cámara {self.rtsp_url}: {e}")

        await self.stop()

    async def add_client(self, websocket):
        if websocket in self.clients:
            return

        print(f"➕ Cliente conectado ({len(self.clients) + 1})")
        if len(self.clients) == 0:
            await self.start()

        task = asyncio.create_task(self._client_sender(websocket))
        self.clients[websocket] = task

    async def _client_sender(self, websocket):
        try:
            while True:
                await asyncio.sleep(1 / 30)
                async with self.frame_lock:
                    if self.latest_frame:
                        await websocket.send_bytes(self.latest_frame)
        except Exception as e:
            print(f"❌ Cliente desconectado: {e}")
        finally:
            await self.remove_client(websocket)

    async def remove_client(self, websocket):
        task = self.clients.pop(websocket, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        print(f"➖ Cliente eliminado ({len(self.clients)} restantes)")

        if not self.clients:
            await self.stop()

    async def stop(self):
        self.running = False
        print(f"🛑 Deteniendo cámara: {self.rtsp_url}")
