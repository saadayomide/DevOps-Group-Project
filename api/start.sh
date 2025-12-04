#!/bin/bash

echo "========================================="
echo "Starting ShopSmart Backend..."
echo "Environment: ${APP_ENV:-development}"
echo "Time: $(date)"
echo "========================================="

# Run database migrations with timeout
echo "[$(date)] Running database migrations..."
timeout 60 python -m alembic upgrade head 2>&1 || {
    echo "[$(date)] WARNING: Migration failed or timed out. Continuing anyway..."
}

echo "[$(date)] Starting Uvicorn server on port 8000..."

# Start the FastAPI application
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
