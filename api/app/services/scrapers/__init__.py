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
- MercadonaScraper: Full Playwright-based implementation
- CarrefourScraper: MVP implementation with mock data
- AlcampoScraper: MVP implementation with mock data

Usage:
    from app.services.scrapers import ScraperManager, get_all_offers

    # Use facade
    manager = ScraperManager()
    offers = manager.get_offers("leche")

    # Or convenience function
    offers = get_all_offers("leche")

    # Individual scrapers
    from app.services.scrapers import scrape_mercadona, scrape_carrefour, scrape_alcampo
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
    "scrape_mercadona",
    "scrape_carrefour",
    "scrape_alcampo",
    # Manager
    "ScraperManager",
    "get_scraper_manager",
    "get_all_offers",
]
