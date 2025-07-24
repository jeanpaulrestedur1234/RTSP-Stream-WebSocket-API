import cv2
import asyncio
import time

class CameraStream:
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.clients = {}  # websocket -> task
        self.running = False
        self.capture = None
        self.latest_frame = None
        self.frame_queue = asyncio.Queue(maxsize=1)
        self.last_reset_time = time.time()

    async def start(self):
        if self.running:
            return
        self.running = True
        self.capture = cv2.VideoCapture(self.rtsp_url)

        if not self.capture.isOpened():
            print(f"❌ No se pudo abrir la cámara: {self.rtsp_url}")
            self.running = False
            return

        print("🎥 Cámara iniciada")
        asyncio.create_task(self._relay_loop())

    async def _relay_loop(self):
        self.capture = cv2.VideoCapture(self.rtsp_url)

        while self.running:

            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)


            # Captura sin leer frames viejos
            self.capture.grab()
            ret, frame = self.capture.retrieve()
            if not ret:
                await asyncio.sleep(0.1)
                continue

            frame = cv2.resize(frame, (640, 360))
            success, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 35])
            if not success:
                continue

            jpeg_bytes = jpeg.tobytes()
            if jpeg_bytes == self.latest_frame:
                print("⚠️ Frame duplicado, omitiendo")
                continue

            self.latest_frame = jpeg_bytes

            # Reemplazar frame anterior
            if self.frame_queue.full():
                _ = await self.frame_queue.get()
            await self.frame_queue.put(jpeg_bytes)

           

            await asyncio.sleep(1 / 15)  # ~15 FPS

    async def add_client(self, websocket):
        if websocket in self.clients:
            return

        print(f"➕ Cliente conectado ({len(self.clients) + 1} total)")
        if len(self.clients) == 0:
            await self.start()

        task = asyncio.create_task(self._client_listener(websocket))
        self.clients[websocket] = task

    async def _client_listener(self, websocket):
        try:
            while True:
                frame = await self.frame_queue.get()
                await websocket.send_bytes(frame)
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
        print(f"➖ Cliente desconectado ({len(self.clients)} restantes)")
        if not self.clients:
            await self.stop()

    async def stop(self):
        self.running = False
        if self.capture:
            self.capture.release()
            self.capture = None
        print("🛑 Cámara detenida")
