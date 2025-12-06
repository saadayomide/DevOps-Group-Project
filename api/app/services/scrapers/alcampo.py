"""
Alcampo scraper implementation (MVP).

Implements BaseScraper interface with minimal but correct functionality.
Due to Sprint 4 time/ethics constraints, this is a shallow implementation
that is structurally correct and fully integrated into ScraperManager.

Design Patterns:
- Adapter: Converts store data to unified Offer format
- Template Method: Inherits from BaseScraper

Best Practices:
- Fails gracefully (returns [])
- Proper logging
- Normalized output
- Never crashes the API
"""

import logging
import time
from typing import List

from .base import BaseScraper, Offer, ScraperFactory, normalize_text, extract_brand

logger = logging.getLogger(__name__)


# MVP Mock Data - simulates scraped products for testing
# Minimal dataset for Sprint 4 demonstration
MOCK_ALCAMPO_PRODUCTS = {
    "leche": [
        {"name": "Leche entera Auchan 1L", "price": 0.79, "brand": "Auchan"},
        {"name": "Leche semidesnatada Puleva 1L", "price": 1.09, "brand": "Puleva"},
        {"name": "Leche sin lactosa Auchan 1L", "price": 1.19, "brand": "Auchan"},
    ],
    "huevos": [
        {"name": "Huevos frescos L Auchan 12 unidades", "price": 2.29, "brand": "Auchan"},
        {"name": "Huevos camperos 6 unidades", "price": 2.69, "brand": "Auchan"},
    ],
    "pan": [
        {"name": "Pan de molde Auchan 450g", "price": 0.99, "brand": "Auchan"},
        {"name": "Barra de pan 250g", "price": 0.65, "brand": None},
    ],
    "arroz": [
        {"name": "Arroz redondo Auchan 1kg", "price": 1.19, "brand": "Auchan"},
        {"name": "Arroz basmati Auchan 500g", "price": 1.59, "brand": "Auchan"},
    ],
    "pasta": [
        {"name": "Espaguetis Auchan 500g", "price": 0.69, "brand": "Auchan"},
        {"name": "Macarrones Auchan 500g", "price": 0.69, "brand": "Auchan"},
    ],
    "aceite": [
        {"name": "Aceite oliva virgen extra Auchan 1L", "price": 6.49, "brand": "Auchan"},
        {"name": "Aceite girasol Auchan 1L", "price": 1.69, "brand": "Auchan"},
    ],
    "yogur": [
        {"name": "Yogur natural Auchan pack 4", "price": 0.99, "brand": "Auchan"},
        {"name": "Yogur griego Auchan pack 4", "price": 1.79, "brand": "Auchan"},
    ],
    "pollo": [
        {"name": "Pechuga pollo Auchan 500g", "price": 4.49, "brand": "Auchan"},
        {"name": "Muslos de pollo kg", "price": 2.99, "brand": None},
    ],
    "tomate": [
        {"name": "Tomate frito Auchan 400g", "price": 0.79, "brand": "Auchan"},
        {"name": "Tomate natural triturado 800g", "price": 0.99, "brand": "Auchan"},
    ],
    "patatas": [
        {"name": "Patatas Auchan bolsa 2kg", "price": 1.99, "brand": "Auchan"},
        {"name": "Patatas fritas Auchan 150g", "price": 1.19, "brand": "Auchan"},
    ],
}


class AlcampoScraper(BaseScraper):
    """
    Alcampo scraper implementing BaseScraper interface.

    MVP Implementation:
    - Uses mock data for reliable testing
    - Follows proper Offer structure
    - Graceful degradation on all errors

    This implementation is minimal but structurally correct,
    demonstrating course concepts (SOLID, patterns) within
    Sprint 4 scope constraints.
    """

    STORE_NAME = "Alcampo"
    BASE_URL = "https://www.alcampo.es"

    def _fetch_products(self, query: str) -> List[Offer]:
        """
        Fetch products matching query (MVP: uses mock data).

        Production implementation would use:
        - Basic GET requests to search endpoint
        - HTML parsing with BeautifulSoup
        - Proper error handling for rate limits
        """
        self.logger.info(f"Searching Alcampo for: {query}")

        # Normalize query for matching
        query_normalized = normalize_text(query)

        # Find matching products from mock data
        offers: List[Offer] = []
        matched_products = []

        # Search in all categories
        for category, products in MOCK_ALCAMPO_PRODUCTS.items():
            category_normalized = normalize_text(category)

            if query_normalized in category_normalized or category_normalized in query_normalized:
                matched_products.extend(products)
            else:
                for product in products:
                    product_normalized = normalize_text(product["name"])
                    if query_normalized in product_normalized:
                        matched_products.append(product)

        # Remove duplicates
        seen_names = set()
        unique_products = []
        for p in matched_products:
            if p["name"] not in seen_names:
                seen_names.add(p["name"])
                unique_products.append(p)

        # Convert to Offer objects
        for product in unique_products:
            offer = Offer(
                store=self.STORE_NAME,
                name=product["name"],
                brand=product.get("brand") or extract_brand(product["name"]),
                price=product["price"],
                url=f"{self.BASE_URL}/search?text={query.replace(' ', '%20')}",
                normalized_name=normalize_text(product["name"]),
            )
            offers.append(offer)

        # Simulate realistic delay
        time.sleep(0.1)

        self.logger.info(f"Found {len(offers)} products for query: {query}")
        return offers


# Register with factory
ScraperFactory.register("alcampo", AlcampoScraper)


def scrape_alcampo(query: str) -> List[Offer]:
    """
    Convenience function for scraping Alcampo.
    Used by debug endpoints and legacy code.

    Args:
        query: Search query

    Returns:
        List of Offer objects
    """
    scraper = AlcampoScraper()
    return scraper.search(query)


# Legacy function for backwards compatibility
def fetch_prices(items: List[dict]) -> List[dict]:
    """
    Legacy interface for backwards compatibility.
    New code should use AlcampoScraper class directly.
    """
    results = []
    for item in items:
        query = item.get("category", "") or item.get("name", "")
        if query:
            offers = scrape_alcampo(query)
            for offer in offers:
                results.append(offer.to_dict())
    return results
