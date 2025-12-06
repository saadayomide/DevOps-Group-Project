"""
Base scraper infrastructure following SOLID principles and design patterns.

Design Patterns:
- Factory Method: ScraperFactory creates scraper instances
- Template Method: BaseScraper defines the scraping algorithm
- Adapter: Each scraper adapts external API to unified Offer format

SOLID Principles:
- SRP: Each scraper handles only its store
- OCP: Adding new stores doesn't modify existing code
- DIP: Services depend on BaseScraper abstraction
"""

import re
import time
import logging
import unicodedata
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Offer(BaseModel):
    """
    Normalized offer returned by all scrapers.
    This is the unified data model that Team B's matching engine consumes.
    """

    store: str = Field(..., description="Store name (e.g., 'Mercadona', 'Carrefour')")
    name: str = Field(..., description="Product name, normalized")
    brand: Optional[str] = Field(None, description="Brand name if available")
    price: float = Field(..., ge=0, description="Price in euros")
    url: Optional[str] = Field(None, description="Product URL for reference")
    image_url: Optional[str] = Field(None, description="Product image URL")
    normalized_name: Optional[str] = Field(
        None, description="Lowercase, accent-free name for matching"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "store": self.store,
            "name": self.name,
            "brand": self.brand,
            "price": self.price,
            "url": self.url,
            "image_url": self.image_url,
            "normalized_name": self.normalized_name,
        }

    class Config:
        json_schema_extra = {
            "example": {
                "store": "Mercadona",
                "name": "Leche Entera Hacendado 1L",
                "brand": "Hacendado",
                "price": 0.89,
                "url": "https://tienda.mercadona.es/product/12345",
                "image_url": "https://example.com/image.jpg",
                "normalized_name": "leche entera hacendado 1l",
            }
        }


def normalize_text(text: str) -> str:
    """
    Normalize text for matching:
    - Remove accents (á -> a, ñ -> n, etc.)
    - Lowercase
    - Collapse whitespace
    - Strip leading/trailing whitespace

    Args:
        text: Raw text to normalize

    Returns:
        Normalized text for matching
    """
    if not text:
        return ""

    # Remove accents using Unicode normalization
    # NFD decomposes characters, then we filter out combining marks
    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    # Lowercase
    normalized = normalized.lower()

    # Collapse whitespace
    normalized = re.sub(r"\s+", " ", normalized)

    # Strip
    normalized = normalized.strip()

    return normalized


def extract_brand(name: str) -> Optional[str]:
    """
    Simple heuristic to extract brand from product name.
    Looks for first capitalized word or known brand patterns.

    Args:
        name: Product name

    Returns:
        Extracted brand or None
    """
    if not name:
        return None

    # Known Spanish supermarket brands
    known_brands = {
        "hacendado",
        "carrefour",
        "alcampo",
        "auchan",
        "dia",
        "eroski",
        "mercadona",
        "lidl",
        "aldi",
        "danone",
        "nestle",
        "pascual",
        "puleva",
        "central lechera",
    }

    name_lower = name.lower()
    for brand in known_brands:
        if brand in name_lower:
            return brand.title()

    # Fallback: first word if it looks like a brand (capitalized, not common word)
    words = name.split()
    if words:
        first_word = words[0]
        # Skip common Spanish product words
        skip_words = {"leche", "pan", "agua", "aceite", "arroz", "pasta", "huevos", "yogur"}
        if first_word.lower() not in skip_words and len(first_word) > 2:
            return first_word

    return None


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.

    Implements Template Method pattern:
    - search() defines the algorithm structure
    - Subclasses implement _fetch_products() and _parse_product()

    All scrapers must:
    1. Handle errors gracefully (return [] on failure)
    2. Log all operations
    3. Return normalized Offer objects
    4. Never crash the API
    """

    STORE_NAME: str = "Unknown"

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def search(self, query: str) -> List[Offer]:
        """
        Template method: Search for products matching query.

        This method handles:
        - Logging
        - Error handling
        - Timing
        - Normalization

        Subclasses implement _fetch_products() for store-specific logic.

        Args:
            query: Search query string

        Returns:
            List of Offer objects, empty list on error (graceful degradation)
        """
        start_time = time.time()
        self.logger.info(f"Starting search for: {query!r}")

        try:
            # Fetch raw products from store
            offers = self._fetch_products(query)

            # Apply normalization to all offers
            for offer in offers:
                if not offer.normalized_name:
                    offer.normalized_name = normalize_text(offer.name)

            elapsed = time.time() - start_time
            self.logger.info(
                f"Search completed: query={query!r}, results={len(offers)}, time={elapsed:.2f}s"
            )

            return offers

        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(
                f"Search failed: query={query!r}, error={str(e)}, time={elapsed:.2f}s",
                exc_info=True,
            )
            # Graceful degradation - return empty list, never crash
            return []

    @abstractmethod
    def _fetch_products(self, query: str) -> List[Offer]:
        """
        Fetch products from the store's API/website.

        Subclasses must implement this method with store-specific logic.
        This method may raise exceptions - they will be caught by search().

        Args:
            query: Search query string

        Returns:
            List of Offer objects
        """
        pass


class ScraperFactory:
    """
    Factory for creating scraper instances.

    Implements Factory Method pattern:
    - Encapsulates scraper creation
    - Allows easy addition of new scrapers
    - Supports dependency injection for testing
    """

    _scrapers: dict = {}

    @classmethod
    def register(cls, store_name: str, scraper_class: type):
        """Register a scraper class for a store"""
        cls._scrapers[store_name.lower()] = scraper_class

    @classmethod
    def create(cls, store_name: str) -> Optional[BaseScraper]:
        """
        Create a scraper instance for the given store.

        Args:
            store_name: Store name (case-insensitive)

        Returns:
            Scraper instance or None if store not found
        """
        scraper_class = cls._scrapers.get(store_name.lower())
        if scraper_class:
            return scraper_class()
        return None

    @classmethod
    def get_available_stores(cls) -> List[str]:
        """Get list of registered store names"""
        return list(cls._scrapers.keys())
