"""
Shopping list orchestrator routes (no scrapers yet).
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import ShoppingList, ShoppingListItem
from app.schemas import (
    ShoppingListCreateRequest,
    ShoppingListResponse,
    ShoppingListItemResponse,
)

router = APIRouter(prefix="/shopping-lists", tags=["Shopping Lists"])


def _to_response(shopping_list: ShoppingList) -> ShoppingListResponse:
    """Map ORM entity to response schema."""
    items: List[ShoppingListItemResponse] = []
    for item in shopping_list.items:
        items.append(
            ShoppingListItemResponse(
                id=item.id,
                category=item.category,
                brand=item.brand,
                variants=item.variants or [],
                quantity=float(item.quantity),
                unit=item.unit,
                best_store=item.best_store,
                best_price=float(item.best_price) if item.best_price is not None else None,
                best_url=item.best_url,
                comparison=item.comparison_json or {},
            )
        )

    return ShoppingListResponse(
        id=shopping_list.id,
        name=shopping_list.name,
        created_at=shopping_list.created_at,
        last_refreshed=shopping_list.last_refreshed,
        items=items,
    )


@router.post("/", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    payload: ShoppingListCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new shopping list with structured items."""
    shopping_list = ShoppingList(name=payload.name)
    db.add(shopping_list)
    db.flush()  # ensure shopping_list.id is available for FK references

    for item in payload.items:
        db_item = ShoppingListItem(
            list_id=shopping_list.id,
            category=item.category,
            brand=item.brand,
            variants=item.variants,
            quantity=item.quantity,
            unit=item.unit,
            spec_json=item.model_dump(),
            best_store=None,
            best_price=None,
            best_url=None,
            comparison_json={},
        )
        shopping_list.items.append(db_item)

    db.commit()
    db.refresh(shopping_list)
    db.refresh(shopping_list, attribute_names=["items"])

    return _to_response(shopping_list)


@router.get("/{list_id}", response_model=ShoppingListResponse)
async def get_shopping_list(
    list_id: int,
    db: Session = Depends(get_db),
):
    """Get a shopping list by ID."""
    shopping_list = (
        db.query(ShoppingList)
        .options(joinedload(ShoppingList.items))
        .filter(ShoppingList.id == list_id)
        .first()
    )
    if shopping_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    return _to_response(shopping_list)


@router.post("/{list_id}/refresh", response_model=ShoppingListResponse)
async def refresh_shopping_list(
    list_id: int,
    db: Session = Depends(get_db),
):
    """
    Placeholder refresh endpoint.
    For now it only bumps last_refreshed to the current time.
    """
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    if shopping_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    shopping_list.last_refreshed = datetime.utcnow()
    db.commit()
    db.refresh(shopping_list)
    db.refresh(shopping_list, attribute_names=["items"])

    return _to_response(shopping_list)
