FROM python:3.12-slim

WORKDIR /app

# No crear archivos .pyc y forzar stdout/stderr sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para pymysql/cryptography
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias primero (cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Railway inyecta PORT como variable de entorno
EXPOSE ${PORT:-8000}

# Ejecutar migraciones y arrancar uvicorn
CMD alembic upgrade head && \
    uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
