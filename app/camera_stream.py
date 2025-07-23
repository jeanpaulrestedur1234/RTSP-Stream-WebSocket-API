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
        while self.running:
            start = time.perf_counter()

            # ⏳ Reiniciar conexión cada 30 segundos
            if time.time() - self.last_reset_time >= 60:
                print("🔁 Reiniciando conexión a cámara (cada 60s)")
                self.capture.release()
                self.capture = cv2.VideoCapture(self.rtsp_url)
                self.last_reset_time = time.time()
                continue

            if not self.capture or not self.capture.isOpened():
                print("🔄 Reintentando conexión a la cámara...")
                self.capture = cv2.VideoCapture(self.rtsp_url)
                self.last_reset_time = time.time()
                continue

            for _ in range(15):  # Limpiar buffer
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
            if jpeg_bytes == self.latest_frame:
                print("⚠️ Frame duplicado, omitiendo")
                continue

            self.latest_frame = jpeg_bytes

            # 📨 Publicar en el canal
            if self.frame_queue.full():
                await self.frame_queue.get()  # Borrar frame viejo
            await self.frame_queue.put(jpeg_bytes)

            duration = time.perf_counter() - start
            if duration > 0.850:
                print(f"⚠️ Demora excesiva ({duration*1000:.1f} ms), reiniciando captura")
                self.capture.release()
                self.capture = None
                self.last_reset_time = time.time()
                continue

            await asyncio.sleep(1 / 100)

        await self.stop()

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
