# ==============================================================================
# Production Dockerfile for CATALYST FastAPI Standalone Backend
# Optimized for Render.com / Cloud Free-Tier (Memory < 512MB)
# ==============================================================================
FROM python:3.11-slim

# Set environment variables for minimal footprint & predictable stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    TORCH_NUM_THREADS=1 \
    OFFLINE_MODE=false \
    ALLOWED_ORIGINS=* \
    PORT=8000

# Install build dependencies for C-extensions (rapidfuzz, sqlite3)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install CPU-only PyTorch and python packages to keep image tiny (<300MB)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/
COPY secrets/ ./secrets/

# Expose port (Render automatically sets $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/v1/system/health || exit 1

# Start Uvicorn
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
