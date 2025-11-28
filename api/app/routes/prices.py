"""
Price routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Price, Product, Supermarket
from app.schemas import Price as PriceSchema, PriceCreate, PriceUpdate

router = APIRouter()


@router.get("/", response_model=List[PriceSchema])
async def get_prices(
    productId: Optional[int] = Query(None, ge=1, description="Filter by product ID"),
    storeId: Optional[int] = Query(None, ge=1, description="Filter by store ID"),
    db: Session = Depends(get_db),
):
    """
    Get prices - handy for debugging
    Query parameters:
    - productId: Optional product ID to filter prices (returns 422 if invalid type)
    - storeId: Optional store ID to filter prices (returns 422 if invalid type)

    FastAPI automatically returns 422 for invalid query parameter types.
    Returns 404 only if path resource is missing (not applicable for this endpoint).
    """
    query = db.query(Price)

    # Apply productId filter if provided
    if productId is not None:
        query = query.filter(Price.product_id == productId)

    # Apply storeId filter if provided
    if storeId is not None:
        query = query.filter(Price.store_id == storeId)

    prices = query.all()
    return prices


@router.get("/{price_id}", response_model=PriceSchema)
async def get_price(price_id: int, db: Session = Depends(get_db)):
    """Get a specific price by ID"""
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Price with id {price_id} not found"
        )
    return price


@router.post("/", response_model=PriceSchema, status_code=status.HTTP_201_CREATED)
async def create_price(price: PriceCreate, db: Session = Depends(get_db)):
    """Create a new price"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == price.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {price.product_id} not found",
        )

    # Verify supermarket (store) exists
    supermarket = db.query(Supermarket).filter(Supermarket.id == price.store_id).first()
    if not supermarket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supermarket (store) with id {price.store_id} not found",
        )

    db_price = Price(**price.model_dump())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price


@router.put("/{price_id}", response_model=PriceSchema)
async def update_price(price_id: int, price: PriceUpdate, db: Session = Depends(get_db)):
    """Update a price"""
    db_price = db.query(Price).filter(Price.id == price_id).first()
    if not db_price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Price with id {price_id} not found"
        )

    # Verify product exists if being updated
    if price.product_id is not None:
        product = db.query(Product).filter(Product.id == price.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {price.product_id} not found",
            )

    # Verify supermarket (store) exists if being updated
    if price.store_id is not None:
        supermarket = db.query(Supermarket).filter(Supermarket.id == price.store_id).first()
        if not supermarket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supermarket (store) with id {price.store_id} not found",
            )

    update_data = price.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_price, field, value)

    db.commit()
    db.refresh(db_price)
    return db_price


@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price(price_id: int, db: Session = Depends(get_db)):
    """Delete a price"""
    db_price = db.query(Price).filter(Price.id == price_id).first()
    if not db_price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Price with id {price_id} not found"
        )

    db.delete(db_price)
    db.commit()
    return None
