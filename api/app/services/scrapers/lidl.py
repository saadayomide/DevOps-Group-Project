"""
Lidl Spain scraper implementation.

Uses Playwright to intercept API responses for reliable data extraction.
Implements BaseScraper interface for unified data acquisition layer.
"""

import asyncio
import logging
import re
from typing import List, Optional

from .base import BaseScraper, Offer, ScraperFactory, normalize_text, extract_brand

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available - Lidl live scraping disabled")

LIDL_BRANDS = ["milbona", "deluxe", "cien", "silvercrest", "parkside", "combino", "snack day"]


def _extract_price_from_text(text: str) -> Optional[float]:
    if not text:
        return None
    match = re.search(r"(\d+[.,]\d+)", str(text))
    if match:
        return float(match.group(1).replace(",", "."))
    return None


def _extract_price(product: dict) -> Optional[float]:
    try:
        price_obj = product.get("price", {})
        if isinstance(price_obj, dict):
            val = price_obj.get("price") or price_obj.get("value")
            if val:
                return float(val)

        for field in ["price", "currentPrice"]:
            val = product.get(field)
            if val is not None and isinstance(val, (int, float)):
                return float(val)
        return None
    except (ValueError, TypeError):
        return None


def _extract_lidl_brand(name: str) -> Optional[str]:
    name_lower = name.lower()
    for brand in LIDL_BRANDS:
        if brand in name_lower:
            return brand.title()
    return extract_brand(name)


async def _search_lidl_playwright(query: str, max_results: int = 20) -> List[dict]:
    if not PLAYWRIGHT_AVAILABLE:
        return []

    products = []
    api_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="es-ES",
        )
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if "search" in url and "api" in url:
                try:
                    if "application/json" in response.headers.get("content-type", ""):
                        data = await response.json()
                        api_responses.append(data)
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            await page.goto(
                f"https://www.lidl.es/q/query/?q={query}", wait_until="networkidle", timeout=30000
            )
            await page.wait_for_timeout(2000)

            for data in api_responses:
                if isinstance(data, dict):
                    prods = (
                        data.get("products", []) or data.get("results", []) or data.get("hits", [])
                    )
                    products.extend(prods)

        except Exception as e:
            logger.warning(f"Playwright Lidl error: {e}")
        finally:
            await browser.close()

    return products[:max_results]


class LidlScraper(BaseScraper):
    STORE_NAME = "Lidl"
    BASE_URL = "https://www.lidl.es"

    def _fetch_products(self, query: str) -> List[Offer]:
        self.logger.info(f"Searching Lidl for: {query}")

        if not PLAYWRIGHT_AVAILABLE:
            return self._fallback_search(query)

        try:
            products = asyncio.run(_search_lidl_playwright(query))

            if products:
                offers = []
                for product in products:
                    keyfacts = product.get("keyfacts", {})
                    name = (
                        keyfacts.get("title")
                        or product.get("fullTitle")
                        or product.get("name")
                        or ""
                    )
                    if not name:
                        continue

                    price = _extract_price(product)
                    if not price or price <= 0:
                        continue

                    offers.append(
                        Offer(
                            store=self.STORE_NAME,
                            name=name,
                            brand=product.get("brand") or _extract_lidl_brand(name),
                            price=float(price),
                            url=product.get("canonicalUrl")
                            or f"{self.BASE_URL}/q/query/?q={query}",
                            image_url=product.get("image"),
                            normalized_name=normalize_text(name),
                        )
                    )

                if offers:
                    self.logger.info(f"Lidl returned {len(offers)} live products")
                    return offers

            return self._fallback_search(query)

        except Exception as e:
            self.logger.warning(f"Lidl error: {e}")
            return self._fallback_search(query)

    def _fallback_search(self, query: str) -> List[Offer]:
        self.logger.info("Using Lidl fallback data")
        fallback_data = {
            "leche": [
                ("Leche entera Milbona 1L", 0.79, "Milbona"),
                ("Leche semidesnatada Milbona 1L", 0.75, "Milbona"),
                ("Leche sin lactosa Milbona 1L", 1.15, "Milbona"),
            ],
            "huevos": [("Huevos frescos M 12 unidades", 2.25, "Lidl")],
            "pan": [("Pan de molde integral 450g", 0.95, "Lidl")],
            "arroz": [("Arroz redondo 1kg", 1.15, "Lidl")],
            "aceite": [("Aceite oliva virgen extra 1L", 6.29, "Lidl")],
            "yogur": [("Yogur natural Milbona pack 4", 0.95, "Milbona")],
            "pasta": [("Espaguetis Combino 500g", 0.65, "Combino")],
            "pollo": [("Pechuga pollo fileteada 500g", 4.45, None)],
            "tomate": [("Tomate frito 400g", 0.75, "Lidl")],
            "agua": [("Agua mineral 6x1.5L", 1.45, "Lidl")],
            "cerveza": [("Cerveza Perlenbacher pack 6", 2.39, "Perlenbacher")],
        }

        query_lower = normalize_text(query)
        offers = []

        for category, products in fallback_data.items():
            if query_lower in category or category in query_lower:
                for name, price, brand in products:
                    offers.append(
                        Offer(
                            store=self.STORE_NAME,
                            name=name,
                            brand=brand,
                            price=price,
                            url=f"{self.BASE_URL}/q/query/?q={query}",
                            normalized_name=normalize_text(name),
                        )
                    )

        if not offers:
            for category, products in fallback_data.items():
                for name, price, brand in products:
                    if query_lower in normalize_text(name):
                        offers.append(
                            Offer(
                                store=self.STORE_NAME,
                                name=name,
                                brand=brand,
                                price=price,
                                url=f"{self.BASE_URL}/q/query/?q={query}",
                                normalized_name=normalize_text(name),
                            )
                        )
        return offers


ScraperFactory.register("lidl", LidlScraper)


def scrape_lidl(query: str) -> List[Offer]:
    return LidlScraper().search(query)
