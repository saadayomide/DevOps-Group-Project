"""
Shopping Lists CRUD Routes

Provides endpoints for:
- POST /shopping-lists: Create a new shopping list
- GET /shopping-lists: List all shopping lists
- GET /shopping-lists/{id}: Get a specific shopping list with items
- DELETE /shopping-lists/{id}: Delete a shopping list
- POST /shopping-lists/{id}/items: Add item to list
- DELETE /shopping-lists/{id}/items/{item_id}: Remove item from list
- POST /shopping-lists/{id}/refresh: Trigger refresh for a shopping list
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

from app.db import get_db
from app.models import ShoppingList, ShoppingListItem
from app.services.refresh_service import async_refresh_shopping_list
import app.db as db_mod
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============ Pydantic Schemas ============


class ShoppingListItemCreate(BaseModel):
    """Schema for creating a shopping list item"""

    name: str = Field(..., description="Product name or search query")
    brand: Optional[str] = Field(None, description="Preferred brand")
    category: Optional[str] = Field(None, description="Product category (milk, eggs, bread, etc.)")
    variants: Optional[str] = Field(
        None, description="Comma-separated variants (e.g., 'desnatada,sin lactosa')"
    )


class ShoppingListItemResponse(BaseModel):
    """Schema for shopping list item response"""

    id: int
    name: str
    brand: Optional[str]
    category: Optional[str]
    variants: Optional[str]
    best_store: Optional[str]
    best_price: Optional[float]
    best_url: Optional[str]
    comparison_json: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ShoppingListCreate(BaseModel):
    """Schema for creating a shopping list"""

    name: str = Field(..., description="List name")
    owner: Optional[str] = Field(None, description="Owner identifier")


class ShoppingListResponse(BaseModel):
    """Schema for shopping list response"""

    id: int
    name: str
    owner: Optional[str]
    last_refreshed: Optional[datetime]
    items: List[ShoppingListItemResponse]

    class Config:
        from_attributes = True


class ShoppingListSummary(BaseModel):
    """Schema for shopping list summary (without items)"""

    id: int
    name: str
    owner: Optional[str]
    last_refreshed: Optional[datetime]
    item_count: int

    class Config:
        from_attributes = True


# ============ Helper Functions ============


def _item_to_response(item: ShoppingListItem) -> ShoppingListItemResponse:
    """Convert ORM item to response schema"""
    return ShoppingListItemResponse(
        id=item.id,
        name=item.name,
        brand=item.brand,
        category=item.category,
        variants=item.variants,
        best_store=item.best_store,
        best_price=float(item.best_price) if item.best_price else None,
        best_url=item.best_url,
        comparison_json=item.comparison_json,
    )


def _list_to_response(sl: ShoppingList) -> ShoppingListResponse:
    """Convert ORM shopping list to response schema"""
    return ShoppingListResponse(
        id=sl.id,
        name=sl.name,
        owner=sl.owner,
        last_refreshed=sl.last_refreshed,
        items=[_item_to_response(item) for item in sl.items],
    )


# ============ Routes ============


@router.post("/", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
def create_shopping_list(data: ShoppingListCreate, db: Session = Depends(get_db)):
    """
    Create a new shopping list.

    The list is created empty. Add items using POST /shopping-lists/{id}/items.
    """
    sl = ShoppingList(name=data.name, owner=data.owner)
    db.add(sl)
    db.commit()
    db.refresh(sl)

    logger.info("Created shopping list id=%s name=%s", sl.id, sl.name)
    return _list_to_response(sl)


@router.get("/", response_model=List[ShoppingListSummary])
def list_shopping_lists(db: Session = Depends(get_db)):
    """
    List all shopping lists with summary info.
    """
    lists = db.query(ShoppingList).all()
    return [
        ShoppingListSummary(
            id=sl.id,
            name=sl.name,
            owner=sl.owner,
            last_refreshed=sl.last_refreshed,
            item_count=len(sl.items),
        )
        for sl in lists
    ]


@router.get("/{list_id}", response_model=ShoppingListResponse)
def get_shopping_list(list_id: int, db: Session = Depends(get_db)):
    """
    Get a shopping list by ID with all items and their comparison results.
    """
    sl = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not sl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Shopping list {list_id} not found"
        )

    return _list_to_response(sl)


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list(list_id: int, db: Session = Depends(get_db)):
    """
    Delete a shopping list and all its items.
    """
    sl = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not sl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Shopping list {list_id} not found"
        )

    # Delete items first (cascade should handle this, but be explicit)
    db.query(ShoppingListItem).filter(ShoppingListItem.shopping_list_id == list_id).delete()
    db.delete(sl)
    db.commit()

    logger.info("Deleted shopping list id=%s", list_id)
    return None


@router.post(
    "/{list_id}/items", response_model=ShoppingListItemResponse, status_code=status.HTTP_201_CREATED
)
def add_item_to_list(list_id: int, data: ShoppingListItemCreate, db: Session = Depends(get_db)):
    """
    Add an item to a shopping list.

    The item will not have comparison results until the list is refreshed.
    """
    sl = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not sl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Shopping list {list_id} not found"
        )

    item = ShoppingListItem(
        shopping_list_id=list_id,
        name=data.name,
        brand=data.brand,
        category=data.category,
        variants=data.variants,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    logger.info("Added item id=%s to list id=%s", item.id, list_id)
    return _item_to_response(item)


@router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_list(list_id: int, item_id: int, db: Session = Depends(get_db)):
    """
    Remove an item from a shopping list.
    """
    item = (
        db.query(ShoppingListItem)
        .filter(ShoppingListItem.id == item_id, ShoppingListItem.shopping_list_id == list_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found in list {list_id}",
        )

    db.delete(item)
    db.commit()

    logger.info("Removed item id=%s from list id=%s", item_id, list_id)
    return None


# ============ Refresh Route ============


async def _run_refresh_background(list_id: int):
    """Background task that creates its own DB session and runs async refresh."""
    db = db_mod.SessionLocal()
    try:
        await async_refresh_shopping_list(list_id, db)
    except Exception as e:
        logger.exception("Background refresh failed for list %s: %s", list_id, e)
    finally:
        db.close()


@router.post("/{list_id}/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_shopping_list(
    list_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Trigger a refresh for a shopping list.

    This endpoint:
    1. Validates the list exists
    2. Schedules a background task to:
       - Build search queries from each item's category/brand/variants
       - Query scrapers for offers
       - Match and score offers
       - Update items with best_store, best_price, best_url, comparison_json
    3. Returns 202 Accepted immediately

    After refresh completes, use GET /shopping-lists/{id} to see updated results.
    """
    # Validate list exists
    sl = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if not sl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Shopping list {list_id} not found"
        )

    # Schedule background refresh
    background_tasks.add_task(_run_refresh_background, list_id)

    logger.info("Scheduled refresh for shopping list id=%s", list_id)
    return {
        "status": "accepted",
        "list_id": list_id,
        "message": "Refresh scheduled. GET /shopping-lists/{id} to see results.",
    }
