"""
Debug endpoints for testing scrapers independently.

These endpoints support developers, QA, and presentation demos.
Always return HTTP 200 to ensure API stability.

Endpoints:
- /api/v1/debug/scrape/mercadona?q=milk
- /api/v1/debug/scrape/carrefour?q=milk
- /api/v1/debug/scrape/alcampo?q=milk
- /api/v1/debug/scrape/all?q=milk
- /api/v1/debug/status

Why these endpoints are important:
- Enables fast debugging
- Used in demos to show real-time data acquisition
- Helps Team B tune matching logic
- Helps Team C display how scrapers behave
"""

import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, Query

from app.services.scrapers import (
    scrape_mercadona,
    scrape_carrefour,
    scrape_alcampo,
    ScraperManager,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/scrape/mercadona")
async def debug_scrape_mercadona(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """
    Debug endpoint for Mercadona scraper.

    Tests Mercadona scraper in isolation.
    Returns raw Offer objects for inspection.
    """
    start_time = time.time()

    try:
        if not q or not q.strip():
            return {
                "store": "Mercadona",
                "query": q,
                "offers": [],
                "count": 0,
                "execution_time_ms": 0,
                "error": "Query cannot be empty",
            }

        offers = scrape_mercadona(q)
        offers_dict = [offer.to_dict() for offer in offers]
        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "store": "Mercadona",
            "query": q,
            "offers": offers_dict,
            "count": len(offers_dict),
            "execution_time_ms": elapsed_ms,
        }

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Debug endpoint error for Mercadona: {str(e)}")
        return {
            "store": "Mercadona",
            "query": q,
            "offers": [],
            "count": 0,
            "execution_time_ms": elapsed_ms,
            "error": str(e),
        }


@router.get("/scrape/carrefour")
async def debug_scrape_carrefour(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """
    Debug endpoint for Carrefour scraper.

    Tests Carrefour scraper in isolation.
    Returns raw Offer objects for inspection.
    """
    start_time = time.time()

    try:
        if not q or not q.strip():
            return {
                "store": "Carrefour",
                "query": q,
                "offers": [],
                "count": 0,
                "execution_time_ms": 0,
                "error": "Query cannot be empty",
            }

        offers = scrape_carrefour(q)
        offers_dict = [offer.to_dict() for offer in offers]
        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "store": "Carrefour",
            "query": q,
            "offers": offers_dict,
            "count": len(offers_dict),
            "execution_time_ms": elapsed_ms,
        }

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Debug endpoint error for Carrefour: {str(e)}")
        return {
            "store": "Carrefour",
            "query": q,
            "offers": [],
            "count": 0,
            "execution_time_ms": elapsed_ms,
            "error": str(e),
        }


@router.get("/scrape/alcampo")
async def debug_scrape_alcampo(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """
    Debug endpoint for Alcampo scraper.

    Tests Alcampo scraper in isolation.
    Returns raw Offer objects for inspection.
    """
    start_time = time.time()

    try:
        if not q or not q.strip():
            return {
                "store": "Alcampo",
                "query": q,
                "offers": [],
                "count": 0,
                "execution_time_ms": 0,
                "error": "Query cannot be empty",
            }

        offers = scrape_alcampo(q)
        offers_dict = [offer.to_dict() for offer in offers]
        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "store": "Alcampo",
            "query": q,
            "offers": offers_dict,
            "count": len(offers_dict),
            "execution_time_ms": elapsed_ms,
        }

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Debug endpoint error for Alcampo: {str(e)}")
        return {
            "store": "Alcampo",
            "query": q,
            "offers": [],
            "count": 0,
            "execution_time_ms": elapsed_ms,
            "error": str(e),
        }


@router.get("/scrape/all")
async def debug_scrape_all(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """
    Debug endpoint to test all scrapers at once.

    Uses ScraperManager facade to fetch from all stores.
    Useful for comparing results across stores.
    """
    start_time = time.time()

    try:
        if not q or not q.strip():
            return {
                "query": q,
                "stores": {},
                "total_offers": 0,
                "execution_time_ms": 0,
                "error": "Query cannot be empty",
            }

        # Use ScraperManager facade
        manager = ScraperManager()
        all_offers = manager.get_offers(q)

        # Group by store
        stores_data: Dict[str, dict] = {}
        for offer in all_offers:
            store = offer.store
            if store not in stores_data:
                stores_data[store] = {"offers": [], "count": 0}
            stores_data[store]["offers"].append(offer.to_dict())
            stores_data[store]["count"] += 1

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "query": q,
            "stores": stores_data,
            "total_offers": len(all_offers),
            "execution_time_ms": elapsed_ms,
        }

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Debug endpoint error for all scrapers: {str(e)}")
        return {
            "query": q,
            "stores": {},
            "total_offers": 0,
            "execution_time_ms": elapsed_ms,
            "error": str(e),
        }


@router.get("/status")
async def debug_scraper_status() -> Dict[str, Any]:
    """
    Get status of all registered scrapers.

    Shows which scrapers are available and operational.
    Useful for monitoring and debugging.
    """
    try:
        manager = ScraperManager()
        status = manager.get_store_status()

        return {
            "status": "ok",
            "scrapers": status,
            "total_scrapers": len(status),
        }

    except Exception as e:
        logger.error(f"Debug status endpoint error: {str(e)}")
        return {
            "status": "error",
            "scrapers": {},
            "total_scrapers": 0,
            "error": str(e),
        }
