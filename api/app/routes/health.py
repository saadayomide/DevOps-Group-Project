"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter()


@router.get("/health")
async def health():
    """Basic health check endpoint - canonical response: {"status": "ok"}"""
    return {"status": "ok"}


@router.get("/health/db")
async def health_db(db: Session = Depends(get_db)):
    """Database health check endpoint that runs a simple query"""
    # Use a simple SELECT to assert DB connectivity
    db.execute("SELECT 1")
    return {"status": "ok"}

