import cv2
import numpy as np
import time

import asyncio
from collections import defaultdict

class CameraStream:
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.clients = {}  # websocket -> asyncio.Queue
        self.running = False
        self.capture = None

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
            if not self.capture or not self.capture.isOpened():
                print("🔄 Reintentando conexión a la cámara...")
                self.capture = cv2.VideoCapture(self.rtsp_url)
                await asyncio.sleep(0.5)
                continue
            for _ in range(10):
                self.capture.read()


            self.capture.grab()  # Avanza sin decodificar
            ret, frame = self.capture.retrieve()
            if not ret:
                print("⚠️ Frame no capturado")
                self.capture.release()
                self.capture = None
                continue

            # ⚡ REDUCIR resolución (mejora tiempo de codificación y red)
            frame = cv2.resize(frame, (640, 360))  # Puedes probar también (480, 270)

            # 🔧 COMPRESIÓN JPEG: reduce tamaño del frame
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Calidad baja-media
            success, jpeg = cv2.imencode('.jpg', frame, encode_param)
            if not success:
                continue

            jpeg_bytes = jpeg.tobytes()

            # 🔥 Publicar una sola vez por frame
            for queue in self.clients.values():
                while not queue.empty():
                    _ = queue.get_nowait()
                await queue.put(jpeg_bytes)

            duration = time.perf_counter() - start
            print(f"📸 Frame enviado a {len(self.clients)} clientes | {duration*1000:.1f} ms")
            if duration > 0.650:
                print(f"⚠️ Demora excesiva ({duration*1000:.1f} ms), reiniciando captura")
                self.capture.release()
                self.capture = None
                continue

            await asyncio.sleep(1 / 24)  # 24 FPS target

        await self.stop()

    async def add_client(self, websocket):
        if websocket in self.clients:
            return

        queue = asyncio.Queue(maxsize=1)
        self.clients[websocket] = queue
        print(f"➕ Cliente conectado ({len(self.clients)} total)")

        # ⬇️ Lanza una tarea por cliente que envía frames desde su cola
        asyncio.create_task(self._client_sender(websocket, queue))

        if len(self.clients) == 1:
            await self.start()

    async def _client_sender(self, websocket, queue):
        try:
            while True:
                frame = await queue.get()
                start = time.perf_counter()
                await websocket.send_bytes(frame)
                delay = time.perf_counter() - start
                if delay > 0.1:
                    print(f"🐢 Cliente lento: {delay:.3f}s")
        except Exception as e:
            print(f"❌ Cliente desconectado: {e}")
            await self.remove_client(websocket)


    async def remove_client(self, websocket):
        if websocket in self.clients:
            del self.clients[websocket]
            print(f"➖ Cliente desconectado ({len(self.clients)} restantes)")
        if not self.clients:
            await self.stop()

    async def stop(self):
        self.running = False
        if self.capture:
            self.capture.release()
            self.capture = None
            print("🛑 Cámara detenida")
