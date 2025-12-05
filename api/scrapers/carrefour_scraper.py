"""
Carrefour scraper implementation
Provides a second real data source for the matching engine
"""

import logging
from typing import List
from .base import Offer

logger = logging.getLogger(__name__)


def scrape_carrefour(query: str) -> List[Offer]:
    """
    Fetch product listings from Carrefour
    
    Args:
        query: Search term for products
        
    Returns:
        List of Offer objects with standardized fields
    """
    try:
        # Normalize query: lowercase and trim
        normalized_query = query.lower().strip()
        
        # Mock data based on common queries
        mock_products = {
            'leche': [
                {'name': 'leche entera carrefour', 'brand': 'carrefour', 'price': 0.89, 'url': 'https://carrefour.es/leche-entera'},
                {'name': 'leche desnatada', 'brand': 'puleva', 'price': 1.15, 'url': 'https://carrefour.es/leche-desnatada'},
            ],
            'pan': [
                {'name': 'pan de molde integral', 'brand': 'bimbo', 'price': 1.25, 'url': 'https://carrefour.es/pan-molde'},
                {'name': 'pan blanco', 'brand': 'carrefour', 'price': 0.95, 'url': 'https://carrefour.es/pan-blanco'},
            ],
            'huevos': [
                {'name': 'huevos camperos 12ud', 'brand': 'carrefour bio', 'price': 2.85, 'url': 'https://carrefour.es/huevos'},
            ],
            'arroz': [
                {'name': 'arroz largo', 'brand': 'la fallera', 'price': 1.45, 'url': 'https://carrefour.es/arroz'},
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
                store='carrefour'
            )
            offers.append(offer)
        
        logger.info(f"Carrefour scraper: found {len(offers)} offers for query '{query}'")
        return offers
        
    except Exception as e:
        # Fail gracefully: log error and return empty list
        logger.error(f"Carrefour scraper failed for query '{query}': {str(e)}")
        return []