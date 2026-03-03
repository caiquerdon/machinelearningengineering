FROM python:3.11-slim

WORKDIR /app

# Evita cache/pyc e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

EXPOSE 8000

# Gunicorn em produção
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.main:app"]
