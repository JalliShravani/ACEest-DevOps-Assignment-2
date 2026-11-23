
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application and tests
COPY app.py .
COPY tests ./tests

# Create non-root user and database directory
RUN useradd --create-home appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/data/aceest.db

EXPOSE 5000

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)"

# Start using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
