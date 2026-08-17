# syntax=docker/dockerfile:1.4
# ==============================================================================
# Uroboros Knowledge Engine: Hardened Backend Microservice Container
# Standard: Zero-Dependency, Multi-Stage, CIS Non-Root Hardened, BuildKit Cached
# ==============================================================================

# Stage 1: Python Dependencies Compiler
FROM python:3.12-slim AS python-builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --prefix=/install -r requirements.txt && \
    find /install -type d -name "tests" -o -type d -name "test" -o -type d -name "__pycache__" | xargs rm -rf 2>/dev/null || true && \
    find /install -type f -name "*.pyc" -o -name "*.pyo" | xargs rm -f 2>/dev/null || true

# Stage 2: Minimal Hardened Runtime Container
FROM python:3.12-slim AS runner
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/local/lib/python3.12/idlelib \
              /usr/local/lib/python3.12/tkinter \
              /usr/local/lib/python3.12/turtledemo \
              /usr/local/lib/python3.12/test 2>/dev/null || true

# Create unprivileged system user for SOC 2 / CIS benchmark compliance (UID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser

# Copy installed Python packages from builder
COPY --from=python-builder /install /usr/local

# Copy application source code
COPY --chown=appuser:appgroup . .

# Ensure storage directories exist with proper non-root permissions and pre-compile bytecode
RUN mkdir -p /app/data /app/dumps /app/vault /app/backups /tmp/cache \
    && python -m compileall -q /app/src \
    && chown -R appuser:appgroup /app /tmp/cache

USER appuser

EXPOSE 8000
EXPOSE 8098/udp

ENV PORT=8000 \
    HOST=0.0.0.0 \
    DB_FILE=/app/data/knowledge.db \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONMALLOC=malloc \
    MALLOC_TRIM_THRESHOLD_=65536 \
    TMPDIR=/tmp/cache

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["uvicorn", "src.app.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "100", "--proxy-headers", "--forwarded-allow-ips=*"]
