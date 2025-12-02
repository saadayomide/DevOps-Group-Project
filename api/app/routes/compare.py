"""
Product comparison routes
Core algorithm: For each requested item, choose the cheapest price across selected stores.
"""

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.orm import Session
import logging
from app.db import get_db
from app.schemas import CompareRequest, CompareResponse
from app.services.compare_service import CompareService

router = APIRouter()
logger = logging.getLogger(__name__)
compare_service = CompareService()


@router.post("/", response_model=CompareResponse)
async def compare_items(request: CompareRequest = Body(...), db: Session = Depends(get_db)):
    """
    Compare items across stores - Core algorithm implementation

    Goal: For each requested item, choose the cheapest price across the selected stores.

    Algorithm (MVP, deterministic):
    1. Normalize items and stores. Reject if empty → 400 BadRequest.
    2. Resolve product IDs by exact name match on LOWER(products.name).
    3. Query all prices for product_id IN (...) and store_id IN (...) in one query.
    4. For each requested item: pick min price with tie-breaker (lower basket subtotal).
    5. Build response arrays: items[], storeTotals[], overallTotal, unmatched[].

    Request body:
    {
        "items": ["milk", "bread", "eggs"],
        "stores": ["Walmart", "Target", "Kroger"]
    }
    """
    # Step 1: Validate request - reject if empty → 400 BadRequest
    if not request.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="items cannot be empty")

    if not request.stores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="stores cannot be empty"
        )

    # Call service to compare basket
    response = compare_service.compare_basket(request, db)

    # Log compare operation with counts (Team C will see this in App Insights)
    items_requested = len(request.items)
    items_matched = len(response.items)
    items_unmatched = len(response.unmatched)

    logger.info(
        "Compare operation completed",
        extra={
            "endpoint": "/compare",
            "method": "POST",
            "items_requested": items_requested,
            "items_matched": items_matched,
            "items_unmatched": items_unmatched,
            "stores_count": len(request.stores),
        },
    )

    return response
