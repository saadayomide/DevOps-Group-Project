"""
Scrapers package for ShopSmart
Handles data retrieval from different supermarkets
"""

from .base import Offer
from .mercadona_scraper import scrape_mercadona
from .carrefour_scraper import scrape_carrefour
from .alcampo_scraper import scrape_alcampo
from .dia_scraper import scrape_dia
from .gadis_scraper import scrape_gadis
from .lidl_scraper import scrape_lidl
from .manager import ScraperManager

__all__ = [
    'Offer',
    'scrape_mercadona',
    'scrape_carrefour',
    'scrape_alcampo',
    'scrape_dia',
    'scrape_gadis',
    'scrape_lidl',
    'ScraperManager',
]