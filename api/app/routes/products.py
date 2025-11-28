"""
Product routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Product
from app.schemas import Product as ProductSchema, ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    q: Optional[str] = Query(None, description="Search query to filter products by name"),
    limit: Optional[int] = Query(
        None, ge=1, le=1000, description="Maximum number of products to return"
    ),
    offset: Optional[int] = Query(None, ge=0, description="Number of products to skip"),
    db: Session = Depends(get_db),
):
    """
    Get all products - returns id and name only (small & consistent response)
    Query parameters:
    - q: Optional search query to filter products by name
    - limit: Optional maximum number of products to return (1-1000, returns 422 if invalid type)
    - offset: Optional number of products to skip (>= 0, returns 422 if invalid type)

    FastAPI automatically returns 422 for invalid query parameter types.
    Returns 404 only if path resource is missing (not applicable for this endpoint).
    """
    query = db.query(Product)

    # Apply search filter if provided
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))

    # Apply offset if provided
    if offset is not None:
        query = query.offset(offset)

    # Apply limit if provided, otherwise use default
    if limit is not None:
        query = query.limit(limit)
    else:
        query = query.limit(100)  # Default limit

    products = query.all()

    # Return only id and name (small & consistent response)
    return [ProductResponse(id=p.id, name=p.name) for p in products]


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID
    Returns 404 if product not found (path resource missing).
    Returns 422 if product_id is not a valid integer (handled automatically by FastAPI).
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found"
        )
    return product


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found"
        )

    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found"
        )

    db.delete(db_product)
    db.commit()
    return None
