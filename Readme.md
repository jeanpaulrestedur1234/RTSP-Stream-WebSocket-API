
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
- 🐳 Soporte para Docker, Docker Compose y Tailscale Funnel

---

## 📁 Estructura del Proyecto

```

.
├── app/
│   ├── main.py              # API FastAPI y conexión WebSocket
│   ├── camera\_stream.py     # Lógica de transmisión de video
│   └── stream\_manager.py    # Manejador de múltiples streams
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── index.html
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
uvicorn app.main:app --host 0.0.0.0 --port 8000
````

---

## 🐳 Uso con Docker Compose

> Requiere que `docker` esté en ejecución y que tengas `tailscale` configurado si vas a usar funnel.

```bash
# 1. Construir imagen
make build

# 2. Levantar contenedor
make up

# 3. Ver logs
make logs

# 4. Acceder vía WebSocket
ws://localhost:8000/ws?rtsp=<RTSP_ENCODED_URL>&camera_index=<ID>
```

> ✅ Este servicio usa `network_mode: host`, por lo que no se necesita mapear puertos en `docker-compose.yml`.

---

## 🌐 Publicar vía Tailscale Funnel

> Asegúrate de tener `tailscale` instalado y en sesión:

```bash
# 1. Iniciar Tailscale (solo si no lo habías hecho)
sudo tailscale up

# 2. Exponer el puerto 8000 públicamente
make funnel
```

Accede desde cualquier navegador o app compatible vía Tailscale.

---

---

## ☸️ Despliegue con Kubernetes y Minikube

> Este proyecto soporta despliegue en clústeres locales Kubernetes usando Minikube con imágenes Docker locales.

### 🧱 Construcción y despliegue

```bash
# 1. Construir imagen en el entorno de Minikube
make k8s-build

# 2. Aplicar los manifiestos Kubernetes
make k8s-deploy

# 3. Ver el estado de los pods
make k8s-status

# 4. Acceder al servicio vía navegador
make k8s-access
```

## 🔌 Conexión WebSocket

```js
const socket = new WebSocket("ws://localhost:8000/ws?rtsp=" + encodeURIComponent("rtsp://192.168.1.100:554/stream1") + "&camera_index=cam1")
```

Parámetros:

* `rtsp`: URL RTSP codificada (usa `encodeURIComponent()` en JS)
* `camera_index`: identificador único para el stream

---

## 🛠️ Troubleshooting

| Problema                         | Solución                                                                   |
| -------------------------------- | -------------------------------------------------------------------------- |
| ❌ No se pudo abrir la cámara     | Verifica que la URL RTSP sea válida y accesible                            |
| 🐢 Cliente lento o congelado     | Reduce resolución o tasa de frames                                         |
| 🐳 Docker no arranca             | Verifica permisos y que Docker esté activo (`sudo systemctl start docker`) |
| 🚫 `containerd` falla al iniciar | Elimina `/run/containerd/containerd.sock` si es un directorio              |

---

## ✅ Requisitos

* Python 3.10 o superior
* FFmpeg (instalado en la imagen Docker)
* Tailscale (para acceso externo opcional)
* Docker y Docker Compose

---

## 📦 Dependencias principales

```text
fastapi
uvicorn
opencv-python-headless
numpy
```

---

## 🧠 Créditos

Desarrollado por **Jean Paul** – para transmisión eficiente de cámaras IP en tiempo real, ideal para sistemas de monitoreo.

---
