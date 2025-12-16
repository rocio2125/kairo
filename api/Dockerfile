# Usamos Python ligero
FROM python:3.9-slim

# Definimos carpeta de trabajo dentro del contenedor
WORKDIR /app

# 1. Copiamos los requerimientos primero (para aprovechar caché)
COPY requirements.txt .

# 2. Instalamos librerías
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos el código de la API
COPY app.py .

# Exponemos el puerto estándar de Flask
EXPOSE 5000

# Ejecutamos la app
# IMPORTANTE: python app.py asume que dentro configuras host='0.0.0.0'
CMD ["python", "app.py"]