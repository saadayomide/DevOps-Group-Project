"""
Catalog routes for static product categories.
"""
from fastapi import APIRouter, HTTPException

from app.services.catalog_service import list_categories, get_category
from app.schemas import CategorySummary, CategoryDetail

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategorySummary])
async def list_catalog_categories():
    """List all catalog categories."""
    categories = list_categories()
    return [CategorySummary(**c) for c in categories]


@router.get("/categories/{code}", response_model=CategoryDetail)
async def get_catalog_category(code: str):
    """Get details for a catalog category."""
    data = get_category(code)
    if data is None:
        raise HTTPException(status_code=404, detail="Unknown category")

    return CategoryDetail(
        code=code,
        label=data["label"],
        units=data.get("units", []),
        variants=data.get("variants", []),
        brands=data.get("brands", []),
    )
