"""
Scraper placeholders to be implemented per retailer.
All scrapers must expose a `fetch_prices(items: list[dict]) -> list[dict]`
that returns a common shape:
[
    {
        "category": "...",
        "brand": "...",
        "variants": [...],
        "quantity": 1.0,
        "unit": "unit",
        "store": "store-name",
        "price": 0.0,
        "url": "https://..."
    }
]
"""

from . import mercadona, carrefour, alcampo  # noqa: F401

__all__ = ["mercadona", "carrefour", "alcampo"]
