"""
Mercadona scraper using Playwright REST API.

This walks /api/categories/, fetches each subcategory, parses products,
matches by query terms, applies semantic filtering, and returns normalized
Offer objects for downstream comparison.
"""
from __future__ import annotations

import logging
import re
import sys
import asyncio
from typing import List, Optional, Tuple

PLAYWRIGHT_AVAILABLE = True
try:
    from playwright.async_api import APIRequestContext, APIResponse, async_playwright
except ImportError:  # pragma: no cover - optional dependency for runtime scraping
    APIRequestContext = None  # type: ignore
    APIResponse = None  # type: ignore
    async_playwright = None  # type: ignore
    PLAYWRIGHT_AVAILABLE = False

# On Windows, the default event loop used by reloader threads can be selector-based,
# which does not support subprocesses (Playwright needs them). Force Proactor policy
# and disable Playwright if needed to avoid NotImplementedError; we'll fall back to httpx.
if sys.platform.startswith("win"):
    try:  # pragma: no cover - platform-specific
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass
    # Prefer httpx path to avoid spawning the browser in environments where subprocess
    # support is limited (e.g., reloader threads).
    async_playwright = None  # type: ignore
    PLAYWRIGHT_AVAILABLE = False

import httpx

from app.services.scrapers.base import Offer

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _extract_number_from_price(text: str) -> Optional[float]:
    """Extract a float from price strings like '1,25 €', '0.79€', etc."""
    if not text:
        return None
    m = re.search(r"(\d+[.,]\d+|\d+)", text)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def _matches_query(name: str, query: str) -> bool:
    """
    Basic matching:
    - lowercase
    - split query into words of length >= 3
    - require ALL those words to be present in the product name
    """
    name_l = name.lower()
    words = [w for w in re.split(r"\s+", query.lower().strip()) if len(w) >= 3]
    if not words:
        return False
    return all(w in name_l for w in words)


def _exclude_wrong_variants(name: str, base: str) -> bool:
    """
    Return True if the product should be excluded due to incompatible variants.
    Example: milk queries should exclude chocolate/batido variants.
    """
    base = base.lower().strip()
    name_l = name.lower()

    forbidden_by_base = {
        "leche": ["chocolate", "cacao", "batido", "cacaolat", "achocolatado"],
    }

    forbidden = forbidden_by_base.get(base, [])
    return any(token in name_l for token in forbidden)


def _ensure_ok(resp: APIResponse, context: str) -> None:
    """Raise with context if Playwright response is not OK."""
    if not resp.ok:
        raise RuntimeError(f"{context} failed with status {resp.status}")


async def _httpx_get_json(client: httpx.AsyncClient, path: str, context: str) -> dict:
    resp = await client.get(path)
    if resp.status_code >= 400:
        raise RuntimeError(f"{context} failed with status {resp.status_code}: {resp.text[:200]}")
    return resp.json()


# --------------------------------------------------------------------------- #
# HTTP calls
# --------------------------------------------------------------------------- #


async def fetch_categories(api: APIRequestContext) -> list:
    resp = await api.get("/api/categories/")
    _ensure_ok(resp, "GET /api/categories/")
    data = await resp.json()
    return data.get("results", [])


async def fetch_category_detail(api: APIRequestContext, category_id: int) -> dict:
    resp = await api.get(f"/api/categories/{category_id}/")
    _ensure_ok(resp, f"GET /api/categories/{category_id}/")
    return await resp.json()


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #


def _collect_products_from_detail(category_detail: dict) -> List[dict]:
    products: List[dict] = []

    direct = category_detail.get("products")
    if isinstance(direct, list) and direct:
        products.extend(direct)

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
) -> List[dict]:
    products_raw = _collect_products_from_detail(category_detail)

    group_name = category_group.get("name", "")
    group_id = category_group.get("id")

    base_subcat_name = category_detail.get("name") or fallback_subcat_name
    base_subcat_id = category_detail.get("id") or fallback_subcat_id

    parsed: List[dict] = []
    for p in products_raw:
        name = p.get("display_name") or p.get("name") or "Sin nombre"
        price_info = p.get("price_instructions", {}) or {}

        numeric_price = (
            price_info.get("unit_price")
            or price_info.get("bulk_price")
            or price_info.get("price")
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
            continue

        nested_name = p.get("_nested_subcategory_name")
        final_subcat_name = nested_name or base_subcat_name

        parsed.append(
            {
                "id": p.get("id"),
                "name": name,
                "price": float(numeric_price),
                "price_raw": price_str,
                "category_name": group_name,
                "subcategory_name": final_subcat_name,
                "category_id": group_id,
                "subcategory_id": base_subcat_id,
                "unit_size": price_info.get("unit_size"),
                "unit_price": price_info.get("reference_price_string")
                or price_info.get("unit_price_string"),
                "slug": p.get("slug"),
            }
        )
    return parsed


# --------------------------------------------------------------------------- #
# High-level search
# --------------------------------------------------------------------------- #


async def search_mercadona_cheapest(
    query: str,
    max_category_groups: Optional[int] = None,
) -> Tuple[Optional[dict], List[dict]]:
    """
    Walk categories and return cheapest + all matches using HTTP client
    to avoid subprocess issues with Playwright on Windows/reload loops.
    """
    all_matches: List[dict] = []
    total_products_scanned = 0

    async with httpx.AsyncClient(base_url="https://tienda.mercadona.es", timeout=30) as client:
        categories_data = await _httpx_get_json(client, "/api/categories/", "GET /api/categories/")
        categories = categories_data.get("results", [])

        if max_category_groups is not None:
            categories = categories[:max_category_groups]

        for group in categories:
            subcats = group.get("categories", []) or []
            for subcat in subcats:
                subcat_id = subcat.get("id")
                subcat_name = subcat.get("name", "")
                if subcat_id is None:
                    continue

                detail = await _httpx_get_json(client, f"/api/categories/{subcat_id}/", f"GET /api/categories/{subcat_id}/")
                products = _parse_category_products(group, detail, subcat_name, subcat_id)
                total_products_scanned += len(products)

                for product in products:
                    if _matches_query(product["name"], query):
                        all_matches.append(product)

    # Debug info (stdout only for manual runs)
    print(f"[mercadona] scanned {total_products_scanned} products, matched {len(all_matches)}")

    if not all_matches:
        return None, []

    all_matches.sort(key=lambda p: p["price"])
    cheapest = all_matches[0]
    return cheapest, all_matches


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def _extract_brand(name: str) -> Optional[str]:
    """
    Simple brand heuristic: pick known private labels, else last token if uppercase.
    """
    name_l = name.lower()
    known = ["hacendado", "carrefour", "alcampo", "eroski", "puleva", "central lechera asturiana"]
    for brand in known:
        if brand in name_l:
            return brand.title()

    parts = name.split()
    if parts and parts[-1].isupper():
        return parts[-1]
    return None


def _ensure_playwright_loaded() -> bool:
    """
    Attempt a late import of playwright if it wasn't available at module import time.
    Returns True if available after this check.
    """
    if sys.platform.startswith("win"):
        return False  # force httpx fallback on Windows to avoid subprocess issues
    global PLAYWRIGHT_AVAILABLE, async_playwright, APIRequestContext, APIResponse  # pylint: disable=global-statement
    if PLAYWRIGHT_AVAILABLE and async_playwright:
        return True
    try:
        from playwright.async_api import APIRequestContext as _APIRequestContext  # type: ignore
        from playwright.async_api import APIResponse as _APIResponse  # type: ignore
        from playwright.async_api import async_playwright as _async_playwright  # type: ignore

        APIRequestContext = _APIRequestContext  # type: ignore
        APIResponse = _APIResponse  # type: ignore
        async_playwright = _async_playwright  # type: ignore
        PLAYWRIGHT_AVAILABLE = True
        return True
    except ImportError:
        PLAYWRIGHT_AVAILABLE = False
        return False


async def search_item(query: str) -> List[Offer]:
    """
    Public entrypoint: return all matching offers for a query.
    Applies semantic filtering before returning.
    """
    try:
        # Try to enable Playwright, otherwise we'll fall back to raw HTTP.
        _ensure_playwright_loaded()
    except Exception as e:  # pragma: no cover - defensive
        logging.exception("Mercadona scraper failed to initialize playwright: %s", e)
        return []

    try:
        _, matches = await search_mercadona_cheapest(query)
    except Exception as e:  # pragma: no cover - runtime safety
        logging.exception("Mercadona scraper failed for query %r: %s", query, e)
        # Return empty list to keep debug endpoint usable instead of 500
        return []

    # Base category inference (very naive): if "leche" in query, apply milk rules.
    base = None
    if "leche" in query.lower():
        base = "leche"

    offers: List[Offer] = []
    for p in matches:
        if base and _exclude_wrong_variants(p["name"], base):
            continue

        offers.append(
            Offer(
                store="mercadona",
                name=p["name"],
                brand=_extract_brand(p["name"]),
                price=p["price"],
                url=f"https://tienda.mercadona.es/product/{p['slug']}" if p.get("slug") else None,
            )
        )

    return offers
