# api/scrapers/gadis_scraper.py
"""
Gadis scraper implementation
Provides additional Galician store source for comparison
"""

import logging
from typing import List
from .base import Offer

logger = logging.getLogger(__name__)


def scrape_gadis(query: str) -> List[Offer]:
    """
    Fetch product listings from Gadis
    
    Args:
        query: Search term for products
        
    Returns:
        List of Offer objects with standardized fields
    """
    try:
        # Normalize query: lowercase and trim
        normalized_query = query.lower().strip()
        
        # Mock data for MVP
        mock_products = {
            'leche': [
                {'name': 'leche entera gadis', 'brand': 'gadis', 'price': 0.88, 'url': 'https://gadis.es/leche-entera'},
                {'name': 'leche semidesnatada', 'brand': 'celta', 'price': 1.12, 'url': 'https://gadis.es/leche-semi'},
                {'name': 'leche entera galega', 'brand': 'larsa', 'price': 1.25, 'url': 'https://gadis.es/leche-galega'},
            ],
            'pan': [
                {'name': 'pan de molde', 'brand': 'gadis', 'price': 1.05, 'url': 'https://gadis.es/pan-molde'},
                {'name': 'pan gallego artesano', 'brand': 'gadis', 'price': 1.45, 'url': 'https://gadis.es/pan-gallego'},
            ],
            'huevos': [
                {'name': 'huevos frescos xl 12ud', 'brand': 'gadis', 'price': 2.65, 'url': 'https://gadis.es/huevos'},
                {'name': 'huevos camperos', 'brand': 'avigal', 'price': 2.95, 'url': 'https://gadis.es/huevos-camperos'},
            ],
            'arroz': [
                {'name': 'arroz redondo', 'brand': 'gadis', 'price': 1.38, 'url': 'https://gadis.es/arroz-redondo'},
                {'name': 'arroz integral', 'brand': 'sos', 'price': 1.75, 'url': 'https://gadis.es/arroz-integral'},
            ],
            'queso': [
                {'name': 'queso tetilla', 'brand': 'gadis', 'price': 3.45, 'url': 'https://gadis.es/queso-tetilla'},
                {'name': 'queso arzua ulloa', 'brand': 'frinsa', 'price': 4.25, 'url': 'https://gadis.es/queso-arzua'},
            ],
            'pulpo': [
                {'name': 'pulpo cocido', 'brand': 'gadis', 'price': 8.95, 'url': 'https://gadis.es/pulpo-cocido'},
            ],
        }
        
        # Find matching products
        results = []
        for key, products in mock_products.items():
            if key in normalized_query or normalized_query in key:
                results.extend(products)
        
        # Convert to Offer objects
        offers = []
        for product in results:
            offer = Offer(
                name=product['name'].lower().strip(),
                brand=product.get('brand', '').lower().strip() if product.get('brand') else '',
                price=product['price'],
                url=product['url'],
                store='gadis'
            )
            offers.append(offer)
        
        logger.info(f"Gadis scraper: found {len(offers)} offers for query '{query}'")
        return offers
        
    except Exception as e:
        # Fail gracefully: log error and return empty list
        logger.error(f"Gadis scraper failed for query '{query}': {str(e)}")
        return []