"""
Temporary debug endpoints for scrapers.
"""
from fastapi import APIRouter, HTTPException

from app.services.scrapers import mercadona

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/scrape/mercadona")
async def debug_scrape(q: str):
    """Debug Mercadona scraper with a query param `q`."""
    try:
        offers = await mercadona.search_item(q)
        return [o.dict() for o in offers]
    except Exception as exc:  # pragma: no cover - debug only
        # Log and return a readable payload instead of 500 to keep Swagger usable
        import logging
        logging.exception("Mercadona scraper debug failed for query %r: %s", q, exc)
        return {"error": "Mercadona scraper error", "detail": str(exc)}
