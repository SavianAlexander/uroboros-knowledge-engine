# Stage 1: Build React Web Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Dependencies Compiler
FROM python:3.12-slim AS python-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 3: Minimal Hardened Runtime Container
FROM python:3.12-slim AS runner
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged system user for SOC 2 / CIS compliance
RUN useradd -m -u 10001 appuser

COPY --from=python-builder /install /usr/local
COPY . .
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

RUN mkdir -p data dumps vault backups \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
EXPOSE 8098/udp

ENV PORT=8000
ENV HOST=0.0.0.0
ENV DB_FILE=/app/data/knowledge.db

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "src.app.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
