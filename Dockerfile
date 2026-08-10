FROM python:3.12-slim

WORKDIR /app

# Install system dependencies that might be needed by some packages (like reportlab, openpyxl, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

# Create necessary directories
RUN mkdir -p dumps vault backups

COPY . .

EXPOSE 8000
EXPOSE 8098/udp

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["uvicorn", "src.app.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
