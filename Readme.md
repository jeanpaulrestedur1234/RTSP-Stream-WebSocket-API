
# 📡 RTSP Stream WebSocket API

Este proyecto permite **retransmitir cámaras RTSP en tiempo real** a través de **WebSockets**, utilizando compresión JPEG y ajuste de resolución para eficiencia.

Ideal para sistemas de videovigilancia, monitoreo remoto o visualización web de cámaras IP.

---

## 🚀 Características

- 🎥 Conexión a cámaras RTSP
- 🔁 Relé de video en tiempo real usando WebSockets
- 📉 Compresión JPEG ajustable
- 🧠 Detección de clientes lentos
- 🧼 Limpieza automática de recursos
- 🐳 Soporte para Docker y despliegue local

---

## 📁 Estructura del Proyecto

```

.
├── app/
│   ├── main.py              # API FastAPI y conexión WebSocket
│   ├── camera\_stream.py     # Lógica de transmisión de video
│   └── stream\_manager.py    # Manejador de múltiples streams
├── Dockerfile
├── requirements.txt
└── README.md

````

---

## 🐍 Instalación Local con `venv`

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8003
````

---

## 🐳 Uso con Docker

```bash
# 1. Construir imagen
docker build -t rtsp-stream-ws .

# 2. Ejecutar contenedor
docker run -p 8003:8003 rtsp-stream-ws
```

---

## 🔌 Conexión WebSocket

Conéctate desde el cliente WebSocket a:

```
ws://localhost:8003/ws?rtsp=<RTSP_ENCODED_URL>&camera_index=<UNIQUE_ID>
```

* `rtsp`: URL de la cámara codificada (usar `encodeURIComponent()` en JS)
* `camera_index`: identificador único para evitar duplicar streams

Ejemplo:

```js
const socket = new WebSocket("ws://localhost:8003/ws?rtsp=" + encodeURIComponent("rtsp://192.168.1.100:554/stream1") + "&camera_index=cam1")
```

---

## 🧪 Recomendaciones

* Prueba con varias cámaras simultáneamente para validar concurrencia.
* Ajusta la resolución (`640x360`) o calidad JPEG en `CameraStream` si hay mucho retardo.
* Usa un cliente WebSocket con capacidad de recibir `bytes` (ej. navegador con `<img>` y canvas, o Python/Node).

---

## ✅ Requisitos

* Python 3.10 o superior
* FFmpeg (solo si deseas procesar más allá de OpenCV)
* Dependencias en `requirements.txt`

---

## 📦 Dependencias

```text
fastapi
uvicorn
opencv-python-headless
numpy
```

---

## 🧠 Créditos

Desarrollado por Jean Paul. Proyecto para transmisión eficiente de cámaras IP en tiempo real.

---

## 🛠️ Troubleshooting

* **❌ No se pudo abrir la cámara**: Verifica que la URL RTSP sea accesible y que no esté siendo usada por otra app.
* **🐢 Cliente lento**: Tu cliente está tardando en recibir o procesar frames; reduce la calidad o resolución.


