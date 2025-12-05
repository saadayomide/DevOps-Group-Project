# api/scrapers/dia_scraper.py
"""
Dia scraper implementation
Provides additional store source for comparison
"""

import logging
from typing import List
from .base import Offer

logger = logging.getLogger(__name__)


def scrape_dia(query: str) -> List[Offer]:
    """
    Fetch product listings from Dia
    
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
                {'name': 'leche entera dia', 'brand': 'dia', 'price': 0.79, 'url': 'https://dia.es/leche-entera'},
                {'name': 'leche desnatada', 'brand': 'president', 'price': 1.09, 'url': 'https://dia.es/leche-desnatada'},
                {'name': 'leche sin lactosa', 'brand': 'kaiku', 'price': 1.35, 'url': 'https://dia.es/leche-sin-lactosa'},
            ],
            'pan': [
                {'name': 'pan de molde blanco', 'brand': 'dia', 'price': 0.85, 'url': 'https://dia.es/pan-molde-blanco'},
                {'name': 'pan integral', 'brand': 'dia', 'price': 1.15, 'url': 'https://dia.es/pan-integral'},
            ],
            'huevos': [
                {'name': 'huevos frescos l 12ud', 'brand': 'dia', 'price': 2.29, 'url': 'https://dia.es/huevos'},
                {'name': 'huevos camperos 6ud', 'brand': 'pazo', 'price': 1.75, 'url': 'https://dia.es/huevos-camperos'},
            ],
            'arroz': [
                {'name': 'arroz largo', 'brand': 'dia', 'price': 1.25, 'url': 'https://dia.es/arroz-largo'},
                {'name': 'arroz integral', 'brand': 'brillante', 'price': 1.89, 'url': 'https://dia.es/arroz-integral'},
            ],
            'pasta': [
                {'name': 'pasta espaguetis', 'brand': 'dia', 'price': 0.69, 'url': 'https://dia.es/espaguetis'},
                {'name': 'pasta macarrones', 'brand': 'gallo', 'price': 0.95, 'url': 'https://dia.es/macarrones'},
            ],
            'aceite': [
                {'name': 'aceite de oliva virgen extra', 'brand': 'dia', 'price': 4.99, 'url': 'https://dia.es/aceite-oliva'},
                {'name': 'aceite de girasol', 'brand': 'coosur', 'price': 2.45, 'url': 'https://dia.es/aceite-girasol'},
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
                store='dia'
            )
            offers.append(offer)
        
        logger.info(f"Dia scraper: found {len(offers)} offers for query '{query}'")
        return offers
        
    except Exception as e:
        # Fail gracefully: log error and return empty list
        logger.error(f"Dia scraper failed for query '{query}': {str(e)}")
        return []