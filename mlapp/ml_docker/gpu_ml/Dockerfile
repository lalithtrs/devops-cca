FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install Vision libraries (libgl1, libglib2) and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install standard PyTorch (GPU version by default on PyPI)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
# Deep Learning APIs usually use Uvicorn/FastAPI instead of Gunicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]