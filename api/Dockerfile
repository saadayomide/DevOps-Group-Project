FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies (if needed by Python packages and Playwright)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only to save space)
RUN playwright install chromium

# Copy application code
COPY app ./app

# Copy Alembic files for migrations
COPY alembic.ini .
COPY alembic ./alembic

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose FastAPI port
EXPOSE 8000

# Environment
ENV PYTHONUNBUFFERED=1

# Start using the startup script which handles migrations
CMD ["./start.sh"]
