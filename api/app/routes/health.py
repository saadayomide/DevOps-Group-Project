"""
Health check endpoints for monitoring and load balancer health probes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import logging

from app.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    database: Optional[str] = None
    version: str = "1.0.0"


class DetailedHealthResponse(BaseModel):
    """Detailed health check response"""

    status: str
    database_status: str
    database_latency_ms: Optional[float] = None
    version: str = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Used by load balancers and container orchestrators
    to verify the service is running.

    Returns:
        HealthResponse with status "ok"
    """
    return HealthResponse(status="ok")


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if the application is running.
    """
    return {"status": "ok", "probe": "liveness"}


@router.get("/health/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe endpoint.

    Checks if the application can handle requests,
    including database connectivity.
    """
    try:
        # Quick DB check
        db.execute(text("SELECT 1"))
        return {"status": "ok", "probe": "readiness", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return {"status": "error", "probe": "readiness", "database": "disconnected"}


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with database connectivity test.

    Useful for debugging and monitoring dashboards.
    """
    import time

    # Test database connectivity
    db_status = "unknown"
    db_latency = None

    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency = (time.time() - start) * 1000  # Convert to ms
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"error: {str(e)}"

    overall_status = "ok" if db_status == "connected" else "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        database_status=db_status,
        database_latency_ms=db_latency,
    )
