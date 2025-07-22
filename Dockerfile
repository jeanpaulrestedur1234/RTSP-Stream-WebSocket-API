FROM python:3.11-slim

# Instala ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY app/ app/

# Puerto expuesto
EXPOSE 8003

# Ejecutar servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
