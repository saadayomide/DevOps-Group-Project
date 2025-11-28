"""
Supermarket routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import Supermarket
from app.schemas import (
    Supermarket as SupermarketSchema,
    SupermarketCreate,
    SupermarketUpdate,
    SupermarketResponse,
)

router = APIRouter()


@router.get("/", response_model=List[SupermarketResponse])
async def get_supermarkets(db: Session = Depends(get_db)):
    """
    Get all supermarkets - returns id and name only (small & consistent response)
    Returns 404 only if path resource is missing (not applicable for this endpoint).
    """
    supermarkets = db.query(Supermarket).all()
    # Return only id and name (small & consistent response)
    return [SupermarketResponse(id=s.id, name=s.name) for s in supermarkets]


@router.get("/{supermarket_id}", response_model=SupermarketSchema)
async def get_supermarket(supermarket_id: int, db: Session = Depends(get_db)):
    """Get a specific supermarket by ID"""
    supermarket = db.query(Supermarket).filter(Supermarket.id == supermarket_id).first()
    if not supermarket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supermarket with id {supermarket_id} not found",
        )
    return supermarket


@router.post("/", response_model=SupermarketSchema, status_code=status.HTTP_201_CREATED)
async def create_supermarket(supermarket: SupermarketCreate, db: Session = Depends(get_db)):
    """Create a new supermarket"""
    # Check if supermarket with same name already exists
    existing = db.query(Supermarket).filter(Supermarket.name == supermarket.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supermarket with name {supermarket.name} already exists",
        )

    db_supermarket = Supermarket(**supermarket.model_dump())
    db.add(db_supermarket)
    db.commit()
    db.refresh(db_supermarket)
    return db_supermarket


@router.put("/{supermarket_id}", response_model=SupermarketSchema)
async def update_supermarket(
    supermarket_id: int, supermarket: SupermarketUpdate, db: Session = Depends(get_db)
):
    """Update a supermarket"""
    db_supermarket = db.query(Supermarket).filter(Supermarket.id == supermarket_id).first()
    if not db_supermarket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supermarket with id {supermarket_id} not found",
        )

    update_data = supermarket.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supermarket, field, value)

    db.commit()
    db.refresh(db_supermarket)
    return db_supermarket


@router.delete("/{supermarket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supermarket(supermarket_id: int, db: Session = Depends(get_db)):
    """Delete a supermarket"""
    db_supermarket = db.query(Supermarket).filter(Supermarket.id == supermarket_id).first()
    if not db_supermarket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supermarket with id {supermarket_id} not found",
        )

    db.delete(db_supermarket)
    db.commit()
    return None
