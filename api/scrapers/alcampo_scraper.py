"""
Alcampo scraper implementation
Provides a third store source for comparison (stub logic for MVP)
"""

import logging
from typing import List
from .base import Offer

logger = logging.getLogger(__name__)


def scrape_alcampo(query: str) -> List[Offer]:
    """
    Fetch product listings from Alcampo
    
    Args:
        query: Search term for products
        
    Returns:
        List of Offer objects with standardized fields
    """
    try:
        # Normalize query: lowercase and trim
        normalized_query = query.lower().strip()
        
        # Mock data for MVP (stub logic acceptable per requirements)
        mock_products = {
            'leche': [
                {'name': 'leche entera alcampo', 'brand': 'alcampo', 'price': 0.85, 'url': 'https://alcampo.es/leche-entera'},
                {'name': 'leche semidesnatada', 'brand': 'pascual', 'price': 1.05, 'url': 'https://alcampo.es/leche-semi'},
            ],
            'pan': [
                {'name': 'pan de molde', 'brand': 'alcampo', 'price': 1.10, 'url': 'https://alcampo.es/pan-molde'},
            ],
            'huevos': [
                {'name': 'huevos frescos 12ud', 'brand': 'alcampo', 'price': 2.45, 'url': 'https://alcampo.es/huevos'},
            ],
            'arroz': [
                {'name': 'arroz redondo', 'brand': 'sos', 'price': 1.35, 'url': 'https://alcampo.es/arroz'},
            ],
        }
        
        # Find matching products
        results = []
        for key, products in mock_products.items():
            if key in normalized_query or normalized_query in key:
                results.extend(products)
        
        # Convert to Offer objects with consistent normalization
        offers = []
        for product in results:
            # Detect brand from name if not explicitly provided
            brand = product.get('brand', '').lower().strip()
            
            offer = Offer(
                name=product['name'].lower().strip(),
                brand=brand,
                price=product['price'],
                url=product['url'],
                store='alcampo'
            )
            offers.append(offer)
        
        logger.info(f"Alcampo scraper: found {len(offers)} offers for query '{query}'")
        return offers
        
    except Exception as e:
        # Fail gracefully: log error and return empty list
        logger.error(f"Alcampo scraper failed for query '{query}': {str(e)}")
        return []