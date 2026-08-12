FROM python:3.12-slim

WORKDIR /app

# Copier et installer les dependances d'abord (meilleur cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code (main.py, model_output/)
COPY . .

# Render fournit le port via la variable $PORT
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]