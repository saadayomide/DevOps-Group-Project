"""
Gadis Spain (Galicia region) scraper implementation.

Uses Playwright to intercept API responses for reliable data extraction.
Implements BaseScraper interface for unified data acquisition layer.

Gadis is a regional supermarket chain primarily operating in Galicia, Spain.
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
    logger.warning("Playwright not available - Gadis live scraping disabled")


def _extract_price_from_text(text: str) -> Optional[float]:
    """Extract price from text like '1,25 €' or '0.79€'."""
    if not text:
        return None
    match = re.search(r"(\d+[.,]\d+)", str(text))
    if match:
        return float(match.group(1).replace(",", "."))
    return None


def _extract_price(product: dict) -> Optional[float]:
    """Extract price from various product data structures."""
    try:
        # Try common price fields
        for field in ["price", "pvp", "precio", "priceValue", "unitPrice"]:
            val = product.get(field)
            if val is not None:
                if isinstance(val, (int, float)):
                    return float(val)
                if isinstance(val, str):
                    return _extract_price_from_text(val)
                if isinstance(val, dict):
                    return float(val.get("value") or val.get("amount") or 0)

        # Try nested prices object
        prices = product.get("prices", {})
        if isinstance(prices, dict):
            for field in ["price", "sale_price", "regular_price"]:
                val = prices.get(field)
                if val is not None:
                    if isinstance(val, dict):
                        return float(val.get("value") or val.get("amount") or 0)
                    return float(val)

        return None
    except (ValueError, TypeError):
        return None


async def _search_gadis_playwright(query: str, max_results: int = 20) -> List[dict]:
    """
    Search Gadis using Playwright with API interception.

    Navigates to Gadis search page and intercepts API responses
    containing product data.
    """
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
            """Intercept API responses containing product data."""
            url = response.url
            # Look for search/product API endpoints
            if any(
                keyword in url.lower()
                for keyword in ["search", "product", "buscar", "catalog", "api"]
            ):
                try:
                    content_type = response.headers.get("content-type", "")
                    if "application/json" in content_type:
                        data = await response.json()
                        api_responses.append(data)
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            # Gadis online store URL
            search_url = f"https://www.gadis.es/buscar?q={query}"
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Extract products from intercepted API responses
            for data in api_responses:
                if isinstance(data, dict):
                    # Try various common response structures
                    prods = (
                        data.get("products", [])
                        or data.get("items", [])
                        or data.get("results", [])
                        or data.get("data", [])
                    )
                    if isinstance(prods, list):
                        products.extend(prods)
                elif isinstance(data, list):
                    products.extend(data)

            # If no API data intercepted, try DOM scraping
            if not products:
                products = await _scrape_gadis_dom(page)

        except Exception as e:
            logger.warning(f"Playwright Gadis error: {e}")
        finally:
            await browser.close()

    return products[:max_results]


async def _scrape_gadis_dom(page) -> List[dict]:
    """
    Fallback DOM scraping if API interception fails.

    Extracts product data directly from the page HTML.
    """
    products = []
    try:
        # Common product card selectors
        product_cards = await page.query_selector_all(
            "[data-product], .product-card, .product-item, .product"
        )

        for card in product_cards[:20]:
            try:
                # Try to extract name
                name_el = await card.query_selector(
                    ".product-name, .product-title, h2, h3, [data-name]"
                )
                name = await name_el.inner_text() if name_el else None

                # Try to extract price
                price_el = await card.query_selector(".product-price, .price, [data-price]")
                price_text = await price_el.inner_text() if price_el else None

                if name and price_text:
                    price = _extract_price_from_text(price_text)
                    if price and price > 0:
                        products.append({"name": name.strip(), "price": price})

            except Exception:
                continue

    except Exception as e:
        logger.debug(f"DOM scraping failed: {e}")

    return products


class GadisScraper(BaseScraper):
    """
    Gadis supermarket scraper.

    Gadis is a regional supermarket chain in Galicia, Spain.
    Uses Playwright for live scraping with fallback to mock data.
    """

    STORE_NAME = "Gadis"
    BASE_URL = "https://www.gadis.es"

    def _fetch_products(self, query: str) -> List[Offer]:
        """Fetch products from Gadis for the given query."""
        self.logger.info(f"Searching Gadis for: {query}")

        if not PLAYWRIGHT_AVAILABLE:
            return self._fallback_search(query)

        try:
            products = asyncio.run(_search_gadis_playwright(query))

            if products:
                offers = []
                for product in products:
                    name = (
                        product.get("name")
                        or product.get("title")
                        or product.get("display_name")
                        or product.get("nombre")
                        or ""
                    )
                    if not name:
                        continue

                    price = _extract_price(product)
                    if not price or price <= 0:
                        continue

                    brand = product.get("brand") or product.get("marca") or extract_brand(name)

                    offers.append(
                        Offer(
                            store=self.STORE_NAME,
                            name=name,
                            brand=brand,
                            price=float(price),
                            url=product.get("url") or f"{self.BASE_URL}/buscar?q={query}",
                            image_url=product.get("image") or product.get("imagen"),
                            normalized_name=normalize_text(name),
                        )
                    )

                if offers:
                    self.logger.info(f"Gadis returned {len(offers)} live products")
                    return offers

            return self._fallback_search(query)

        except Exception as e:
            self.logger.warning(f"Gadis error: {e}")
            return self._fallback_search(query)

    def _fallback_search(self, query: str) -> List[Offer]:
        """
        Return mock data when live scraping fails.

        Provides realistic Galician regional product data.
        """
        self.logger.info("Using Gadis fallback data")

        # Gadis-specific fallback data with Galician regional products
        fallback_data = {
            "leche": [
                ("Leche entera Gadis 1L", 0.79, "Gadis"),
                ("Leche Larsa semidesnatada 1L", 1.15, "Larsa"),
                ("Leche Feiraco entera 1L", 1.05, "Feiraco"),
                ("Leche sin lactosa Gadis 1L", 1.19, "Gadis"),
            ],
            "huevos": [
                ("Huevos camperos Gadis L docena", 2.89, "Gadis"),
                ("Huevos frescos M 12 unidades", 2.29, None),
            ],
            "pan": [
                ("Pan de molde Gadis 450g", 0.95, "Gadis"),
                ("Pan gallego artesano 500g", 1.45, None),
            ],
            "arroz": [
                ("Arroz redondo Gadis 1kg", 1.15, "Gadis"),
                ("Arroz largo SOS 1kg", 1.69, "SOS"),
            ],
            "aceite": [
                ("Aceite oliva virgen extra Gadis 1L", 6.49, "Gadis"),
                ("Aceite oliva Carbonell 1L", 7.25, "Carbonell"),
            ],
            "yogur": [
                ("Yogur natural Gadis pack 4", 0.95, "Gadis"),
                ("Yogur Larsa sabores pack 4", 1.29, "Larsa"),
            ],
            "pasta": [
                ("Espaguetis Gadis 500g", 0.65, "Gadis"),
                ("Macarrones Gadis 500g", 0.65, "Gadis"),
            ],
            "pollo": [
                ("Pechuga pollo Gadis 500g", 4.49, "Gadis"),
                ("Muslos de pollo 600g", 3.29, None),
            ],
            "tomate": [
                ("Tomate frito Gadis 400g", 0.79, "Gadis"),
                ("Tomate natural triturado 780g", 1.19, None),
            ],
            "agua": [
                ("Agua mineral Cabreiroá 6x1.5L", 2.19, "Cabreiroá"),
                ("Agua Mondariz 6x1.5L", 2.49, "Mondariz"),
            ],
            "queso": [
                ("Queso tetilla Gadis 400g", 4.95, "Gadis"),
                ("Queso Arzúa-Ulloa DOP 500g", 6.49, None),
            ],
            "pescado": [
                ("Sardinas frescas 500g", 3.49, None),
                ("Merluza fresca rodajas 400g", 5.99, None),
            ],
            "marisco": [
                ("Mejillones gallegos 1kg", 3.99, None),
                ("Pulpo cocido 300g", 8.99, None),
            ],
            "vino": [
                ("Vino Albariño Rias Baixas 75cl", 6.99, None),
                ("Vino Ribeiro blanco 75cl", 4.49, None),
            ],
            "cerveza": [
                ("Cerveza Estrella Galicia pack 6", 4.29, "Estrella Galicia"),
                ("Cerveza 1906 pack 6", 5.99, "1906"),
            ],
        }

        query_lower = normalize_text(query)
        offers = []

        # First try exact category match
        for category, products in fallback_data.items():
            if query_lower in category or category in query_lower:
                for name, price, brand in products:
                    offers.append(
                        Offer(
                            store=self.STORE_NAME,
                            name=name,
                            brand=brand,
                            price=price,
                            url=f"{self.BASE_URL}/buscar?q={query}",
                            normalized_name=normalize_text(name),
                        )
                    )

        # If no category match, try name matching
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
                                url=f"{self.BASE_URL}/buscar?q={query}",
                                normalized_name=normalize_text(name),
                            )
                        )

        return offers


# Register with factory
ScraperFactory.register("gadis", GadisScraper)


def scrape_gadis(query: str) -> List[Offer]:
    """Convenience function to scrape Gadis."""
    return GadisScraper().search(query)
