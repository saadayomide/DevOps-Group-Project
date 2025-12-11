"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime
from app.db import SessionLocal

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint - used by smoke tests"""
    return {"status": "ok"}


@router.get("/health/db")
async def database_health_check():
    """Database health check endpoint"""
    try:
        from sqlalchemy import text

        db = SessionLocal()
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
