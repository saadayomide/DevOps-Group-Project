"""
Debug endpoints for testing scrapers independently
"""

from fastapi import APIRouter, Query
from typing import Dict, Any
import logging
import sys
from pathlib import Path

# Add parent directory to path to import scrapers
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scrapers import (
    scrape_mercadona, 
    scrape_carrefour, 
    scrape_alcampo,
    scrape_dia,
    scrape_gadis,
    scrape_lidl
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/scrape/mercadona")
async def debug_scrape_mercadona(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Debug endpoint for Mercadona scraper"""
    try:
        if not q or not q.strip():
            return {"store": "mercadona", "query": q, "offers": [], "count": 0, "error": "Query cannot be empty"}
        
        offers = scrape_mercadona(q)
        offers_dict = [offer.to_dict() for offer in offers]
        
        return {"store": "mercadona", "query": q, "offers": offers_dict, "count": len(offers_dict)}
        
    except Exception as e:
        logger.error(f"Debug endpoint error for Mercadona: {str(e)}")
        return {"store": "mercadona", "query": q, "offers": [], "count": 0, "error": str(e)}


@router.get("/scrape/carrefour")
async def debug_scrape_carrefour(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Debug endpoint for Carrefour scraper"""
    try:
        if not q or not q.strip():
            return {"store": "carrefour", "query": q, "offers": [], "count": 0, "error": "Query cannot be empty"}
        
        offers = scrape_carrefour(q)
        offers_dict = [offer.to_dict() for offer in offers]
        
        return {"store": "carrefour", "query": q, "offers": offers_dict, "count": len(offers_dict)}
        
    except Exception as e:
        logger.error(f"Debug endpoint error for Carrefour: {str(e)}")
        return {"store": "carrefour", "query": q, "offers": [], "count": 0, "error": str(e)}


@router.get("/scrape/alcampo")
async def debug_scrape_alcampo(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Debug endpoint for Alcampo scraper"""
    try:
        if not q or not q.strip():
            return {"store": "alcampo", "query": q, "offers": [], "count": 0, "error": "Query cannot be empty"}
        
        offers = scrape_alcampo(q)
        offers_dict = [offer.to_dict() for offer in offers]
        
        return {"store": "alcampo", "query": q, "offers": offers_dict, "count": len(offers_dict)}
        
    except Exception as e:
        logger.error(f"Debug endpoint error for Alcampo: {str(e)}")
        return {"store": "alcampo", "query": q, "offers": [], "count": 0, "error": str(e)}


@router.get("/scrape/dia")
async def debug_scrape_dia(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Debug endpoint for Dia scraper"""
    try:
        if not q or not q.strip():
            return {"store": "dia", "query": q, "offers": [], "count": 0, "error": "Query cannot be empty"}
        
        offers = scrape_dia(q)
        offers_dict = [offer.to_dict() for offer in offers]
        
        return {"store": "dia", "query": q, "offers": offers_dict, "count": len(offers_dict)}
        
    except Exception as e:
        logger.error(f"Debug endpoint error for Dia: {str(e)}")
        return {"store": "dia", "query": q, "offers": [], "count": 0, "error": str(e)}


@router.get("/scrape/gadis")
async def debug_scrape_gadis(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Debug endpoint for Gadis scraper"""
    try:
        if not q or not q.strip():
            return {"store": "gadis", "query": q, "offers": [], "count": 0, "error": "Query cannot be empty"}
        
        offers = scrape_gadis(q)
        offers_dict = [offer.to_dict() for offer in offers]
        
        return {"store": "gadis", "query": q, "offers": offers_dict, "count": len(offers_dict)}
        
    except Exception as e:
        logger.error(f"Debug endpoint error for Gadis: {str(e)}")
        return {"store": "gadis", "query": q, "offers": [], "count": 0, "error": str(e)}


@router.get("/scrape/lidl")
async def debug_scrape_lidl(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """Debug endpoint for Lidl scraper"""
    try:
        if not q or not q.strip():
            return {"store": "lidl", "query": q, "offers": [], "count": 0, "error": "Query cannot be empty"}
        
        offers = scrape_lidl(q)
        offers_dict = [offer.to_dict() for offer in offers]
        
        return {"store": "lidl", "query": q, "offers": offers_dict, "count": len(offers_dict)}
        
    except Exception as e:
        logger.error(f"Debug endpoint error for Lidl: {str(e)}")
        return {"store": "lidl", "query": q, "offers": [], "count": 0, "error": str(e)}


@router.get("/scrape/all")
async def debug_scrape_all(q: str = Query(..., description="Search query")) -> Dict[str, Any]:
    """
    Debug endpoint to test all scrapers at once
    Useful for comparing results across stores
    """
    try:
        if not q or not q.strip():
            return {"query": q, "stores": {}, "total_offers": 0, "error": "Query cannot be empty"}
        
        # Scrape all stores
        mercadona_offers = scrape_mercadona(q)
        carrefour_offers = scrape_carrefour(q)
        alcampo_offers = scrape_alcampo(q)
        dia_offers = scrape_dia(q)
        gadis_offers = scrape_gadis(q)
        lidl_offers = scrape_lidl(q)
        
        result = {
            "query": q,
            "stores": {
                "mercadona": {
                    "offers": [offer.to_dict() for offer in mercadona_offers],
                    "count": len(mercadona_offers)
                },
                "carrefour": {
                    "offers": [offer.to_dict() for offer in carrefour_offers],
                    "count": len(carrefour_offers)
                },
                "alcampo": {
                    "offers": [offer.to_dict() for offer in alcampo_offers],
                    "count": len(alcampo_offers)
                },
                "dia": {
                    "offers": [offer.to_dict() for offer in dia_offers],
                    "count": len(dia_offers)
                },
                "gadis": {
                    "offers": [offer.to_dict() for offer in gadis_offers],
                    "count": len(gadis_offers)
                },
                "lidl": {
                    "offers": [offer.to_dict() for offer in lidl_offers],
                    "count": len(lidl_offers)
                }
            },
            "total_offers": (
                len(mercadona_offers) + len(carrefour_offers) + len(alcampo_offers) + 
                len(dia_offers) + len(gadis_offers) + len(lidl_offers)
            )
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Debug endpoint error for all scrapers: {str(e)}")
        return {"query": q, "stores": {}, "total_offers": 0, "error": str(e)}