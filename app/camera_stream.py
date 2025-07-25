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
        self.frame_lock = asyncio.Lock()  # Protección para acceso concurrente
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
        frame_count = 0
        last_fps_time = time.time()

        while self.running:
            for _ in range(5):  # Puedes bajar a 3 o 5 si quieres menos latencia
                self.capture.read()

            self.capture.grab()
            ret, frame = self.capture.retrieve()
            if not ret:
                continue

            frame = cv2.resize(frame, (640, 360))
            success, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            if not success:
                continue

            jpeg_bytes = jpeg.tobytes()

            async with self.frame_lock:
                self.latest_frame = jpeg_bytes

            frame_count += 1
            current_time = time.time()
            if current_time - last_fps_time >= 1:
                print(f"📦 FPS enviados: {frame_count}")
                frame_count = 0
                last_fps_time = current_time

            await asyncio.sleep(1 / 30)  # Intenta 30 FPS

        await self.stop()

    async def add_client(self, websocket):
        if websocket in self.clients:
            return

        print(f"➕ Cliente conectado ({len(self.clients) + 1} total)")
        if len(self.clients) == 0:
            await self.start()

        task = asyncio.create_task(self._client_sender(websocket))
        self.clients[websocket] = task

    async def _client_sender(self, websocket):
        try:
            while True:
                await asyncio.sleep(1 / 30)  # Ritmo de envío
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
        print(f"➖ Cliente desconectado ({len(self.clients)} restantes)")
        if not self.clients:
            await self.stop()

    async def stop(self):
        self.running = False
        if self.capture:
            self.capture.release()
            self.capture = None
        print("🛑 Cámara detenida")