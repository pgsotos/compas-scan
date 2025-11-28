# Multi-stage Dockerfile for CompasScan API
# Stage 1: Builder - Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim

WORKDIR /app

# Create non-root user first
RUN useradd -m -u 1000 compas

# Copy Python dependencies from builder to user's home
COPY --from=builder /root/.local /home/compas/.local

# Make sure scripts in .local are usable
ENV PATH=/home/compas/.local/bin:$PATH

# Copy application code
COPY api/ ./api/
COPY test_local.py .

# Set ownership
RUN chown -R compas:compas /app /home/compas/.local
USER compas

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start server
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]

