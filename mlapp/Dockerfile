# Use an official lightweight Python base image
FROM python:3.11-slim

# Set environment variables for Python performance and output buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    PYTHONPATH=/app/src

# Set working directory inside container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application directories into container
COPY data/ ./data/
COPY models/ ./models/
COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/

# Create a non-root user for security compliance
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose application port
EXPOSE 5000

# Health check to ensure service vitality
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Start production application server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "src.app:app"]
