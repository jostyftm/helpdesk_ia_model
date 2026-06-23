# Usa una imagen base oficial de Python ligera
FROM python:3.12-slim

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los requerimientos e instálalos aprovechando la caché de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente y los modelos serializados
COPY . .

# Expone el puerto que utilizará FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación en producción
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]