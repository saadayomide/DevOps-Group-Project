"""
Mercadona scraper implementation.

Uses Playwright's APIRequestContext to fetch data from Mercadona's internal API.
Implements BaseScraper interface for unified data acquisition layer.

Design Patterns:
- Adapter: Converts Mercadona API response to unified Offer format
- Template Method: Inherits from BaseScraper

Error Handling:
- All errors are logged and return empty list (graceful degradation)
- API timeouts and blocks are handled gracefully
- Never crashes the matching engine
"""

import asyncio
import re
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .base import BaseScraper, Offer, ScraperFactory, normalize_text, extract_brand

logger = logging.getLogger(__name__)

# Check if Playwright is available (optional dependency)
try:
    from playwright.async_api import async_playwright, APIRequestContext, APIResponse

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available - Mercadona live scraping disabled")


# ---- Internal Data Model --------------------------------------------------------


@dataclass
class MercadonaProduct:
    """Internal representation of Mercadona product data"""

    id: int
    name: str
    price: float
    price_raw: str
    category_name: str
    subcategory_name: str
    category_id: int
    subcategory_id: int
    unit_size: Optional[str] = None
    unit_price: Optional[str] = None
    slug: Optional[str] = None


# ---- Helper Functions -----------------------------------------------------------


def _extract_number_from_price(text: str) -> Optional[float]:
    """
    Extract a float from price strings like '1,25 €', '0.79€', etc.
    Returns None if no number is found.
    """
    if not text:
        return None
    m = re.search(r"(\d+[.,]\d+|\d+)", text)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def _matches_query(name: str, query: str) -> bool:
    """
    Check if product name matches search query.
    - Lowercases everything
    - Splits query into words of length >= 3
    - Requires ALL those words to be present in product name
    """
    name_l = normalize_text(name)
    query_normalized = normalize_text(query)

    # Words of 3+ chars to avoid matching "de", "y", etc.
    words = [w for w in query_normalized.split() if len(w) >= 3]
    if not words:
        return False
    return all(w in name_l for w in words)


async def _ensure_ok(resp: "APIResponse", context: str) -> None:
    """Validate API response status"""
    if not resp.ok:
        try:
            body = await resp.text()
        except Exception:
            body = "<failed to read body>"
        raise RuntimeError(f"{context} failed with status {resp.status}: {body[:300]}")


# ---- API Functions --------------------------------------------------------------


async def fetch_categories(api: "APIRequestContext") -> list:
    """Fetch /api/categories/ and return the 'results' list."""
    resp = await api.get("/api/categories/")
    await _ensure_ok(resp, "GET /api/categories/")
    data = await resp.json()
    return data["results"]


async def fetch_category_detail(api: "APIRequestContext", category_id: int) -> dict:
    """Fetch a single category's full JSON from /api/categories/{id}/"""
    resp = await api.get(f"/api/categories/{category_id}/")
    await _ensure_ok(resp, f"GET /api/categories/{category_id}/")
    return await resp.json()


# ---- Parsing Functions ----------------------------------------------------------


def _collect_products_from_detail(category_detail: dict) -> List[dict]:
    """
    Collect all products from category detail.
    Handles both direct products and nested subcategories.
    """
    products: List[dict] = []

    # Case 1: direct products list
    direct = category_detail.get("products")
    if isinstance(direct, list) and direct:
        products.extend(direct)

    # Case 2: nested subcategories with their own 'products'
    nested_cats = category_detail.get("categories") or []
    for sub in nested_cats:
        sub_products = sub.get("products") or []
        for p in sub_products:
            p["_nested_subcategory_name"] = sub.get("name")
        products.extend(sub_products)

    return products


def _parse_category_products(
    category_group: dict,
    category_detail: dict,
    fallback_subcat_name: str,
    fallback_subcat_id: int,
) -> List[MercadonaProduct]:
    """Parse products from a category_detail payload."""
    products_raw = _collect_products_from_detail(category_detail)

    group_name = category_group["name"]
    group_id = category_group["id"]

    base_subcat_name = category_detail.get("name") or fallback_subcat_name
    base_subcat_id = category_detail.get("id") or fallback_subcat_id

    parsed: List[MercadonaProduct] = []

    for p in products_raw:
        name = p.get("display_name") or p.get("name") or "Sin nombre"

        price_info = p.get("price_instructions", {}) or {}

        numeric_price = (
            price_info.get("unit_price") or price_info.get("bulk_price") or price_info.get("price")
        )

        price_str = (
            price_info.get("bulk_price_string")
            or price_info.get("unit_price_string")
            or price_info.get("price_string")
            or ""
        )

        if numeric_price is None:
            numeric_price = _extract_number_from_price(price_str)

        if numeric_price is None:
            # No price we can trust → skip
            continue

        nested_name = p.get("_nested_subcategory_name")
        final_subcat_name = nested_name or base_subcat_name

        product = MercadonaProduct(
            id=p.get("id"),
            name=name,
            price=float(numeric_price),
            price_raw=price_str,
            category_name=group_name,
            subcategory_name=final_subcat_name,
            category_id=group_id,
            subcategory_id=base_subcat_id,
            unit_size=price_info.get("unit_size"),
            unit_price=price_info.get("reference_price_string")
            or price_info.get("unit_price_string"),
            slug=p.get("slug"),
        )
        parsed.append(product)

    return parsed


# ---- High-Level Search ----------------------------------------------------------


async def search_mercadona_cheapest(
    query: str,
    max_category_groups: Optional[int] = None,
) -> Tuple[Optional[MercadonaProduct], List[MercadonaProduct]]:
    """
    Search Mercadona products via their API.

    Args:
        query: Search query
        max_category_groups: Limit categories to search (for speed)

    Returns:
        Tuple of (cheapest_product, all_matches)
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright not available, returning empty results")
        return None, []

    async with async_playwright() as p:
        api = await p.request.new_context(base_url="https://tienda.mercadona.es")

        categories = await fetch_categories(api)

        if max_category_groups is not None:
            categories = categories[:max_category_groups]

        all_matches: List[MercadonaProduct] = []
        total_products_scanned = 0

        for group in categories:
            subcats = group.get("categories", []) or []

            for subcat in subcats:
                subcat_id = subcat["id"]
                subcat_name = subcat.get("name", "")

                detail = await fetch_category_detail(api, subcat_id)
                products = _parse_category_products(group, detail, subcat_name, subcat_id)

                total_products_scanned += len(products)

                for product in products:
                    if _matches_query(product.name, query):
                        all_matches.append(product)

        logger.info(
            f"Scanned ~{total_products_scanned} products "
            f"across {len(categories)} top-level groups."
        )

        if not all_matches:
            return None, []

        all_matches.sort(key=lambda p: p.price)
        cheapest = all_matches[0]
        return cheapest, all_matches


# ---- BaseScraper Implementation -------------------------------------------------


class MercadonaScraper(BaseScraper):
    """
    Mercadona scraper implementing BaseScraper interface.

    Features:
    - Uses Playwright's APIRequestContext for reliable API access
    - Normalizes product names for matching
    - Extracts brand information
    - Handles errors gracefully (returns [] on failure)
    """

    STORE_NAME = "Mercadona"
    BASE_URL = "https://tienda.mercadona.es"

    def _fetch_products(self, query: str) -> List[Offer]:
        """
        Fetch products from Mercadona API.
        Runs async code in sync context for BaseScraper interface.
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not available - returning empty results")
            return []

        # Run async search in sync context
        _, matches = asyncio.run(search_mercadona_cheapest(query, max_category_groups=5))

        # Convert MercadonaProduct to Offer (Adapter pattern)
        offers: List[Offer] = []
        for product in matches[:20]:  # Limit to top 20 results
            offer = Offer(
                store=self.STORE_NAME,
                name=product.name,
                brand=extract_brand(product.name),
                price=product.price,
                url=f"{self.BASE_URL}/product/{product.slug}" if product.slug else None,
                normalized_name=normalize_text(product.name),
            )
            offers.append(offer)

        return offers


# Register with factory
ScraperFactory.register("mercadona", MercadonaScraper)


# ---- Convenience Function (backwards compatibility) -----------------------------


def scrape_mercadona(query: str) -> List[Offer]:
    """
    Convenience function for scraping Mercadona.
    Used by debug endpoints and legacy code.

    Args:
        query: Search query

    Returns:
        List of Offer objects
    """
    scraper = MercadonaScraper()
    return scraper.search(query)
