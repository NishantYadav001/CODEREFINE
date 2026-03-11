# ════════════════════════════════════════════════════════════════════
# CODEREFINE - Dockerfile
# ════════════════════════════════════════════════════════════════════
# Production-ready container image for CodeRefine AI Platform
# Uses Python 3.11 slim base for minimal footprint
# ════════════════════════════════════════════════════════════════════

# STAGE 1: Builder Stage (if needed for optimization)
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# STAGE 2: Final Runtime Stage
FROM python:3.11-slim

# ────────────────────────────────────────────────────────────────────
# Environment Variables
# ────────────────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PATH=/root/.local/bin:$PATH

# Set non-root user for security
ENV APP_USER=appuser

# ────────────────────────────────────────────────────────────────────
# System Dependencies
# ────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OCR & Image Processing
    tesseract-ocr \
    # Image dependencies
    libgl1 \
    libglib2.0-0 \
    # Health check utilities
    curl \
    # PDF generation dependencies
    libpng16-16 \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ────────────────────────────────────────────────────────────────────
# Create Non-Root User for Security
# ────────────────────────────────────────────────────────────────────
RUN useradd -m -u 1000 ${APP_USER} && \
    mkdir -p /app/logs && \
    chown -R ${APP_USER}:${APP_USER} /app

# ────────────────────────────────────────────────────────────────────
# Application Setup
# ────────────────────────────────────────────────────────────────────
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} backend/ ./backend/
COPY --chown=${APP_USER}:${APP_USER} frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R ${APP_USER}:${APP_USER} /app/logs /app/data

# ────────────────────────────────────────────────────────────────────
# Switch to Non-Root User
# ────────────────────────────────────────────────────────────────────
USER ${APP_USER}

# ────────────────────────────────────────────────────────────────────
# Port Exposure
# ────────────────────────────────────────────────────────────────────
EXPOSE 8000

# ────────────────────────────────────────────────────────────────────
# Health Check
# ────────────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# ────────────────────────────────────────────────────────────────────
# Application Entry Point
# ────────────────────────────────────────────────────────────────────
WORKDIR /app/backend

CMD ["python", "main.py"]

# ════════════════════════════════════════════════════════════════════
# BUILD INSTRUCTIONS
# ════════════════════════════════════════════════════════════════════
# docker build -t coderefine:latest .
# docker run -p 8000:8000 --env-file .env coderefine:latest
# ════════════════════════════════════════════════════════════════════