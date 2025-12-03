#!/bin/bash
set -e

echo "Starting ShopSmart Backend..."
echo "Environment: ${APP_ENV:-development}"

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head || {
    echo "Migration failed or no migrations to run, continuing..."
}

echo "Migrations complete. Starting server..."

# Start the FastAPI application
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
