"""
Supermarket Scrapers Package - Unified Data Acquisition Layer

This package implements Team A's scraper infrastructure following:
- SOLID principles (SRP, OCP, DIP)
- Design patterns (Factory, Adapter, Facade, Template Method)
- DevOps best practices (logging, error tolerance)

Components:
- BaseScraper: Abstract base class for all scrapers
- Offer: Normalized data model for scraped products
- ScraperFactory: Factory for creating scraper instances
- ScraperManager: Facade that unifies all scrapers

Available Scrapers:
- MercadonaScraper: Full Playwright-based live implementation
- CarrefourScraper: Playwright API with fallback
- AlcampoScraper: Playwright API with fallback
- LidlScraper: Playwright API with fallback
- DiaScraper: Playwright API with fallback
- GadisScraper: Playwright API with fallback (Galicia region)

Usage:
    from app.services.scrapers import ScraperManager, get_all_offers

    # Use facade
    manager = ScraperManager()
    offers = manager.get_offers("leche")

    # Or convenience function
    offers = get_all_offers("leche")

    # Individual scrapers
    from app.services.scrapers import scrape_mercadona, scrape_carrefour
    mercadona_offers = scrape_mercadona("huevos")
"""

# Base classes and models
from .base import (
    Offer,
    BaseScraper,
    ScraperFactory,
    normalize_text,
    extract_brand,
)

# Individual scrapers
from .mercadona import MercadonaScraper, scrape_mercadona
from .carrefour import CarrefourScraper, scrape_carrefour
from .alcampo import AlcampoScraper, scrape_alcampo
from .lidl import LidlScraper, scrape_lidl
from .dia import DiaScraper, scrape_dia
from .gadis import GadisScraper, scrape_gadis

# Manager (Facade)
from .manager import (
    ScraperManager,
    get_scraper_manager,
    get_all_offers,
)

__all__ = [
    # Base
    "Offer",
    "BaseScraper",
    "ScraperFactory",
    "normalize_text",
    "extract_brand",
    # Scrapers
    "MercadonaScraper",
    "CarrefourScraper",
    "AlcampoScraper",
    "LidlScraper",
    "DiaScraper",
    "GadisScraper",
    "scrape_mercadona",
    "scrape_carrefour",
    "scrape_alcampo",
    "scrape_lidl",
    "scrape_dia",
    "scrape_gadis",
    # Manager
    "ScraperManager",
    "get_scraper_manager",
    "get_all_offers",
]
