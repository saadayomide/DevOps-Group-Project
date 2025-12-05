# api/scrapers/manager.py
"""
Scraper Manager - Central orchestrator for all scrapers
Handles parallel/sequential scraping with error handling
"""

import logging
from typing import List
from .base import Offer
from .mercadona_scraper import scrape_mercadona
from .carrefour_scraper import scrape_carrefour
from .alcampo_scraper import scrape_alcampo
from .dia_scraper import scrape_dia
from .gadis_scraper import scrape_gadis
from .lidl_scraper import scrape_lidl

logger = logging.getLogger(__name__)


class ScraperManager:
    """
    Central orchestrator used by Team B to gather all store offers
    Ensures every scraper is wrapped in timeouts, try/except, no unhandled exceptions
    """
    
    # Map of store names to scraper functions
    SCRAPERS = {
        'mercadona': scrape_mercadona,
        'carrefour': scrape_carrefour,
        'alcampo': scrape_alcampo,
        'dia': scrape_dia,
        'gadis': scrape_gadis,
        'lidl': scrape_lidl,
    }
    
    @classmethod
    def get_offers(cls, query: str, stores: List[str] = None) -> List[Offer]:
        """
        Fetch offers from multiple stores for a given query
        
        Args:
            query: Search term for products
            stores: List of store names to query (if None, queries all stores)
            
        Returns:
            Combined list of offers from all requested stores
            
        Note:
            Sequential execution for Sprint 4 (async-lite acceptable)
            Real parallelism reserved for Sprint 5
        """
        if not query or not query.strip():
            logger.warning("Empty query provided to ScraperManager")
            return []
        
        # Use all scrapers if no specific stores requested
        if stores is None:
            stores = list(cls.SCRAPERS.keys())
        
        all_offers = []
        
        # Sequential scraping (acceptable for Sprint 4 per requirements)
        for store in stores:
            if store not in cls.SCRAPERS:
                logger.warning(f"Unknown store '{store}' requested, skipping")
                continue
            
            try:
                scraper_func = cls.SCRAPERS[store]
                
                # Call scraper with timeout protection
                # Each scraper already has its own error handling
                offers = scraper_func(query)
                
                # Validate offers before adding
                if offers and isinstance(offers, list):
                    all_offers.extend(offers)
                    logger.info(f"ScraperManager: got {len(offers)} offers from {store}")
                else:
                    logger.warning(f"ScraperManager: no valid offers from {store}")
                    
            except Exception as e:
                # Catch any unhandled exceptions to ensure no crashes
                logger.error(f"ScraperManager: unhandled error from {store}: {str(e)}")
                # Continue to next scraper instead of failing
                continue
        
        logger.info(f"ScraperManager: total {len(all_offers)} offers from {len(stores)} stores")
        return all_offers
    
    @classmethod
    def get_available_stores(cls) -> List[str]:
        """Get list of all available store scrapers"""
        return list(cls.SCRAPERS.keys())