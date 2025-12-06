"""
Carrefour scraper implementation (MVP).

Implements BaseScraper interface with MVP-level functionality.
Due to Sprint 4 time constraints, this provides basic mock data
with proper structure for testing the matching engine.

Design Patterns:
- Adapter: Converts store data to unified Offer format
- Template Method: Inherits from BaseScraper

Course-Relevant Concepts:
- SRP: Handles only Carrefour scraping
- OCP: Adding new stores doesn't modify this code
- Graceful degradation: Always returns structured response
"""

import logging
import time
from typing import List

from .base import BaseScraper, Offer, ScraperFactory, normalize_text, extract_brand

logger = logging.getLogger(__name__)


# MVP Mock Data - simulates scraped products for testing
# In production, this would be replaced with actual HTTP/HTML scraping
MOCK_CARREFOUR_PRODUCTS = {
    "leche": [
        {"name": "Leche entera Carrefour 1L", "price": 0.85, "brand": "Carrefour"},
        {"name": "Leche semidesnatada Carrefour 1L", "price": 0.82, "brand": "Carrefour"},
        {"name": "Leche desnatada Pascual 1L", "price": 1.15, "brand": "Pascual"},
        {"name": "Leche sin lactosa Central Lechera 1L", "price": 1.35, "brand": "Central Lechera"},
    ],
    "huevos": [
        {"name": "Huevos frescos M Carrefour docena", "price": 2.45, "brand": "Carrefour"},
        {"name": "Huevos camperos L 6 unidades", "price": 2.85, "brand": "Carrefour"},
        {"name": "Huevos ecológicos 6 unidades", "price": 3.49, "brand": "Bio"},
    ],
    "pan": [
        {"name": "Pan de molde integral Carrefour 450g", "price": 1.25, "brand": "Carrefour"},
        {"name": "Barra de pan rústica", "price": 0.95, "brand": None},
        {"name": "Pan Bimbo familiar 700g", "price": 2.35, "brand": "Bimbo"},
    ],
    "arroz": [
        {"name": "Arroz largo Carrefour 1kg", "price": 1.35, "brand": "Carrefour"},
        {"name": "Arroz basmati 500g", "price": 1.89, "brand": "Carrefour"},
        {"name": "Arroz integral 1kg", "price": 1.75, "brand": "Carrefour"},
    ],
    "pasta": [
        {"name": "Espaguetis Carrefour 500g", "price": 0.79, "brand": "Carrefour"},
        {"name": "Macarrones Gallo 500g", "price": 1.15, "brand": "Gallo"},
        {"name": "Pasta fresca tortellini 250g", "price": 2.49, "brand": "Rana"},
    ],
    "aceite": [
        {"name": "Aceite oliva virgen extra Carrefour 1L", "price": 6.95, "brand": "Carrefour"},
        {"name": "Aceite oliva suave Carrefour 1L", "price": 5.49, "brand": "Carrefour"},
        {"name": "Aceite girasol Carrefour 1L", "price": 1.89, "brand": "Carrefour"},
    ],
    "yogur": [
        {"name": "Yogur natural Carrefour pack 4", "price": 1.15, "brand": "Carrefour"},
        {"name": "Yogur griego Danone 4x125g", "price": 2.49, "brand": "Danone"},
        {"name": "Yogur sabores Carrefour pack 8", "price": 1.89, "brand": "Carrefour"},
    ],
    "pollo": [
        {"name": "Pechuga pollo fileteada 500g", "price": 4.95, "brand": None},
        {"name": "Muslos de pollo bandeja", "price": 3.25, "brand": None},
        {"name": "Pollo entero 1.5kg", "price": 5.49, "brand": None},
    ],
    "tomate": [
        {"name": "Tomate frito Carrefour 400g", "price": 0.89, "brand": "Carrefour"},
        {"name": "Tomate triturado 800g", "price": 1.15, "brand": "Carrefour"},
        {"name": "Tomate rama kg", "price": 1.99, "brand": None},
    ],
    "patatas": [
        {"name": "Patatas bolsa 3kg", "price": 2.49, "brand": None},
        {"name": "Patatas nuevas 1kg", "price": 1.35, "brand": None},
        {"name": "Patatas fritas bolsa 150g", "price": 1.49, "brand": "Lays"},
    ],
}


class CarrefourScraper(BaseScraper):
    """
    Carrefour scraper implementing BaseScraper interface.

    MVP Implementation:
    - Uses mock data for reliable testing
    - Follows proper Offer structure
    - Demonstrates Adapter pattern

    Production would implement:
    - HTML scraping with BeautifulSoup/lxml
    - Or REST API calls if available
    """

    STORE_NAME = "Carrefour"
    BASE_URL = "https://www.carrefour.es"

    def _fetch_products(self, query: str) -> List[Offer]:
        """
        Fetch products matching query (MVP: uses mock data).

        In production, this would:
        1. Make HTTP request to Carrefour search API/page
        2. Parse HTML/JSON response
        3. Extract product data
        4. Convert to Offer format
        """
        self.logger.info(f"Searching Carrefour for: {query}")

        # Normalize query for matching
        query_normalized = normalize_text(query)

        # Find matching products from mock data
        offers: List[Offer] = []
        matched_products = []

        # Search in all categories
        for category, products in MOCK_CARREFOUR_PRODUCTS.items():
            category_normalized = normalize_text(category)

            # Check if query matches category or search in all if generic
            if query_normalized in category_normalized or category_normalized in query_normalized:
                matched_products.extend(products)
            else:
                # Also check individual product names
                for product in products:
                    product_normalized = normalize_text(product["name"])
                    if query_normalized in product_normalized:
                        matched_products.append(product)

        # Remove duplicates (by name)
        seen_names = set()
        unique_products = []
        for p in matched_products:
            if p["name"] not in seen_names:
                seen_names.add(p["name"])
                unique_products.append(p)

        # Convert to Offer objects (Adapter pattern)
        for product in unique_products:
            offer = Offer(
                store=self.STORE_NAME,
                name=product["name"],
                brand=product.get("brand") or extract_brand(product["name"]),
                price=product["price"],
                url=f"{self.BASE_URL}/search?q={query.replace(' ', '+')}",
                normalized_name=normalize_text(product["name"]),
            )
            offers.append(offer)

        # Simulate realistic delay
        time.sleep(0.1)

        self.logger.info(f"Found {len(offers)} products for query: {query}")
        return offers


# Register with factory
ScraperFactory.register("carrefour", CarrefourScraper)


def scrape_carrefour(query: str) -> List[Offer]:
    """
    Convenience function for scraping Carrefour.
    Used by debug endpoints and legacy code.

    Args:
        query: Search query

    Returns:
        List of Offer objects
    """
    scraper = CarrefourScraper()
    return scraper.search(query)


# Legacy function for backwards compatibility
def fetch_prices(items: List[dict]) -> List[dict]:
    """
    Legacy interface for backwards compatibility.
    New code should use CarrefourScraper class directly.
    """
    results = []
    for item in items:
        query = item.get("category", "") or item.get("name", "")
        if query:
            offers = scrape_carrefour(query)
            for offer in offers:
                results.append(offer.to_dict())
    return results
