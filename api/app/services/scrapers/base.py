"""
Common scraper types.
"""
from typing import Optional
from pydantic import BaseModel


class Offer(BaseModel):
    """Normalized offer returned by scrapers."""
    store: str
    name: str
    brand: Optional[str] = None
    price: float
    url: Optional[str] = None
