"""
Base classes and data models for scrapers
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Offer:
    """
    Standardized product offer structure
    All scrapers must return data in this format
    """
    name: str              # Product name (normalized: lowercase, trimmed)
    price: float           # Price in euros
    store: str             # Store identifier (e.g., "mercadona", "carrefour")
    url: str               # Product URL
    brand: str = ""        # Brand name (normalized: lowercase, trimmed)
    
    def to_dict(self):
        """Convert offer to dictionary for API responses"""
        return {
            'name': self.name,
            'brand': self.brand,
            'price': self.price,
            'url': self.url,
            'store': self.store
        }