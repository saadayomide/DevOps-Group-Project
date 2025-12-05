# api/scrapers/lidl_scraper.py
"""
Lidl scraper implementation
Provides German discount store source for comparison
"""

import logging
from typing import List
from .base import Offer

logger = logging.getLogger(__name__)


def scrape_lidl(query: str) -> List[Offer]:
    """
    Fetch product listings from Lidl
    
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
                {'name': 'leche entera milbona', 'brand': 'milbona', 'price': 0.75, 'url': 'https://lidl.es/leche-entera'},
                {'name': 'leche desnatada', 'brand': 'milbona', 'price': 0.99, 'url': 'https://lidl.es/leche-desnatada'},
                {'name': 'leche sin lactosa', 'brand': 'milbona', 'price': 1.29, 'url': 'https://lidl.es/leche-sin-lactosa'},
            ],
            'pan': [
                {'name': 'pan de molde sandwich', 'brand': 'dulano', 'price': 0.79, 'url': 'https://lidl.es/pan-molde'},
                {'name': 'pan integral multicereales', 'brand': 'dulano', 'price': 1.19, 'url': 'https://lidl.es/pan-multicereales'},
            ],
            'huevos': [
                {'name': 'huevos frescos m 10ud', 'brand': 'lidl', 'price': 1.99, 'url': 'https://lidl.es/huevos'},
                {'name': 'huevos camperos 6ud', 'brand': 'lidl', 'price': 1.49, 'url': 'https://lidl.es/huevos-camperos'},
            ],
            'arroz': [
                {'name': 'arroz largo', 'brand': 'golden sun', 'price': 1.19, 'url': 'https://lidl.es/arroz-largo'},
                {'name': 'arroz basmati', 'brand': 'golden sun', 'price': 1.79, 'url': 'https://lidl.es/arroz-basmati'},
            ],
            'yogur': [
                {'name': 'yogur natural pack 8', 'brand': 'milbona', 'price': 1.25, 'url': 'https://lidl.es/yogur-natural'},
                {'name': 'yogur griego', 'brand': 'milbona', 'price': 1.89, 'url': 'https://lidl.es/yogur-griego'},
            ],
            'chocolate': [
                {'name': 'chocolate con leche', 'brand': 'fin carre', 'price': 0.99, 'url': 'https://lidl.es/chocolate-leche'},
                {'name': 'chocolate negro 85%', 'brand': 'j.d.gross', 'price': 1.49, 'url': 'https://lidl.es/chocolate-negro'},
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
                store='lidl'
            )
            offers.append(offer)
        
        logger.info(f"Lidl scraper: found {len(offers)} offers for query '{query}'")
        return offers
        
    except Exception as e:
        # Fail gracefully: log error and return empty list
        logger.error(f"Lidl scraper failed for query '{query}': {str(e)}")
        return []