"""
Mercadona scraper implementation
This is your existing scraper - keeping it for consistency
"""

import logging
from typing import List
from .base import Offer

logger = logging.getLogger(__name__)


def scrape_mercadona(query: str) -> List[Offer]:
    """
    Fetch product listings from Mercadona
    
    Args:
        query: Search term for products
        
    Returns:
        List of Offer objects with standardized fields
    """
    try:
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Mock data for MVP
        mock_products = {
            'leche': [
                {'name': 'leche entera hacendado', 'brand': 'hacendado', 'price': 0.92, 'url': 'https://mercadona.es/leche-entera'},
                {'name': 'leche semidesnatada', 'brand': 'central lechera', 'price': 1.20, 'url': 'https://mercadona.es/leche-semi'},
            ],
            'pan': [
                {'name': 'pan de molde integral', 'brand': 'hacendado', 'price': 1.30, 'url': 'https://mercadona.es/pan-molde'},
                {'name': 'pan blanco', 'brand': 'hacendado', 'price': 1.00, 'url': 'https://mercadona.es/pan-blanco'},
            ],
            'huevos': [
                {'name': 'huevos frescos l 12ud', 'brand': 'hacendado', 'price': 2.50, 'url': 'https://mercadona.es/huevos'},
            ],
            'arroz': [
                {'name': 'arroz largo', 'brand': 'hacendado', 'price': 1.50, 'url': 'https://mercadona.es/arroz'},
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
                brand=product.get('brand', '').lower().strip(),
                price=product['price'],
                url=product['url'],
                store='mercadona'
            )
            offers.append(offer)
        
        logger.info(f"Mercadona scraper: found {len(offers)} offers for query '{query}'")
        return offers
        
    except Exception as e:
        logger.error(f"Mercadona scraper failed for query '{query}': {str(e)}")
        return []