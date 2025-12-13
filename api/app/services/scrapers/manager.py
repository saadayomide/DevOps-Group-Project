"""
ScraperManager - Unified Facade for all supermarket scrapers.

This is the most critical component of Team A's work.
Implements the Facade pattern to provide a single interface
for all scraping operations.

Design Patterns:
- Facade: Simplifies subsystem complexity
- Factory: Uses ScraperFactory for scraper creation

SOLID Principles:
- DIP: Depends on BaseScraper abstraction, not concrete implementations
- OCP: Adding new stores requires no changes to this class

Why this is best practice:
- Team B only calls ScraperManager.get_offers(query)
- If a store breaks, the system still works
- Adding new supermarkets requires no refactoring outside Team A
"""

import logging
import time
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseScraper, Offer, ScraperFactory

# Import scrapers to register them with factory
from . import mercadona, carrefour, alcampo, lidl, dia, gadis  # noqa: F401

logger = logging.getLogger(__name__)


class ScraperManager:
    """
    Unified facade for all supermarket scrapers.

    Responsibilities:
    - Accept query string from matching engine (Team B)
    - Call all registered scrapers
    - Combine results into unified list
    - Log per-store failures without aborting
    - Ensure consistent output format

    Usage:
        manager = ScraperManager()
        offers = manager.get_offers("leche")
        # Returns List[Offer] from all stores
    """

    def __init__(self, stores: Optional[List[str]] = None):
        """
        Initialize ScraperManager.

        Args:
            stores: Optional list of store names to use.
                    If None, uses all registered stores.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Get available stores from factory
        available_stores = ScraperFactory.get_available_stores()

        if stores:
            # Filter to requested stores (case-insensitive)
            self.stores = [s.lower() for s in stores if s.lower() in available_stores]
        else:
            self.stores = available_stores

        # Create scraper instances
        self.scrapers: Dict[str, BaseScraper] = {}
        for store in self.stores:
            scraper = ScraperFactory.create(store)
            if scraper:
                self.scrapers[store] = scraper

        self.logger.info(f"ScraperManager initialized with stores: {list(self.scrapers.keys())}")

    def get_offers(self, query: str) -> List[Offer]:
        """
        Get offers from all stores for the given query.

        This is the main entry point for Team B's matching engine.
        Combines results from all scrapers into a single list.

        Features:
        - Calls all scrapers
        - Combines results
        - Logs per-store failures without aborting
        - Never crashes (graceful degradation)

        Args:
            query: Search query string

        Returns:
            Combined list of Offer objects from all stores
        """
        start_time = time.time()
        self.logger.info(
            f"ScraperManager: Starting search for '{query}' across {len(self.scrapers)} stores"
        )

        all_offers: List[Offer] = []
        store_results: Dict[str, int] = {}
        store_errors: Dict[str, str] = {}

        # Search each store (sequentially for simplicity)
        for store_name, scraper in self.scrapers.items():
            try:
                store_start = time.time()
                offers = scraper.search(query)
                store_elapsed = time.time() - store_start

                all_offers.extend(offers)
                store_results[store_name] = len(offers)

                self.logger.info(f"{store_name}: {len(offers)} results in {store_elapsed:.2f}s")

            except Exception as e:
                # Log error but continue with other stores
                store_errors[store_name] = str(e)
                store_results[store_name] = 0
                self.logger.error(
                    f"ScraperManager: {store_name} failed with error: {e}", exc_info=True
                )

        elapsed = time.time() - start_time

        # Log summary
        self.logger.info(
            f"ScraperManager: Search completed - query='{query}', "
            f"total_results={len(all_offers)}, "
            f"stores={store_results}, "
            f"errors={len(store_errors)}, "
            f"time={elapsed:.2f}s"
        )

        return all_offers

    def get_offers_parallel(self, query: str, max_workers: int = 3) -> List[Offer]:
        """
        Get offers from all stores in parallel (experimental).

        Uses ThreadPoolExecutor for concurrent scraping.
        More performant but may hit rate limits.

        Args:
            query: Search query string
            max_workers: Maximum concurrent scrapers

        Returns:
            Combined list of Offer objects from all stores
        """
        start_time = time.time()
        self.logger.info(
            f"ScraperManager: Starting parallel search for '{query}' "
            f"across {len(self.scrapers)} stores"
        )

        all_offers: List[Offer] = []
        store_results: Dict[str, int] = {}

        def search_store(store_name: str, scraper: BaseScraper) -> tuple:
            """Worker function for parallel execution"""
            try:
                offers = scraper.search(query)
                return (store_name, offers, None)
            except Exception as e:
                return (store_name, [], str(e))

        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(search_store, name, scraper): name
                for name, scraper in self.scrapers.items()
            }

            for future in as_completed(futures):
                store_name, offers, error = future.result()
                if error:
                    self.logger.error(f"ScraperManager: {store_name} failed: {error}")
                    store_results[store_name] = 0
                else:
                    all_offers.extend(offers)
                    store_results[store_name] = len(offers)

        elapsed = time.time() - start_time
        self.logger.info(
            f"ScraperManager: Parallel search completed - "
            f"total_results={len(all_offers)}, time={elapsed:.2f}s"
        )

        return all_offers

    def get_offers_by_store(self, query: str, store: str) -> List[Offer]:
        """
        Get offers from a specific store only.

        Useful for debugging and testing individual scrapers.

        Args:
            query: Search query string
            store: Store name (case-insensitive)

        Returns:
            List of Offer objects from the specified store
        """
        store_lower = store.lower()
        scraper = self.scrapers.get(store_lower)

        if not scraper:
            self.logger.warning(
                f"Store '{store}' not found. Available: {list(self.scrapers.keys())}"
            )
            return []

        return scraper.search(query)

    def get_store_status(self) -> Dict[str, dict]:
        """
        Get status of all registered scrapers.

        Returns:
            Dict with store names as keys and status info as values
        """
        status = {}
        for store_name, scraper in self.scrapers.items():
            status[store_name] = {
                "name": scraper.STORE_NAME,
                "available": True,
                "class": scraper.__class__.__name__,
            }
        return status


# Singleton instance for convenience
_default_manager: Optional[ScraperManager] = None


def get_scraper_manager() -> ScraperManager:
    """
    Get the default ScraperManager instance (singleton).

    Returns:
        ScraperManager instance with all stores
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = ScraperManager()
    return _default_manager


def get_all_offers(query: str) -> List[Offer]:
    """
    Convenience function to get offers from all stores.

    Args:
        query: Search query

    Returns:
        List of Offer objects from all stores
    """
    return get_scraper_manager().get_offers(query)
