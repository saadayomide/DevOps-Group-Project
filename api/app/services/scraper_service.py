"""
Scraper service to fetch prices from supermarkets and update the database.
"""

import asyncio
import logging
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Product, Supermarket, Price
from app.services.scrapers.mercadona import search_mercadona_cheapest

logger = logging.getLogger(__name__)


class ScraperService:
    """Service to orchestrate scraping and database updates"""

    STORE_NAME = "Mercadona"

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_supermarket(self, name: str, city: str = "Madrid") -> Supermarket:
        """Get existing supermarket or create new one"""
        store = self.db.query(Supermarket).filter(Supermarket.name.ilike(name)).first()

        if not store:
            store = Supermarket(name=name, city=city)
            self.db.add(store)
            self.db.commit()
            self.db.refresh(store)
            logger.info(f"Created new supermarket: {name}")

        return store

    def get_or_create_product(self, name: str, category: str) -> Product:
        """Get existing product or create new one"""
        # Try exact match first
        product = self.db.query(Product).filter(Product.name.ilike(name)).first()

        if not product:
            product = Product(name=name, category=category)
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            logger.info(f"Created new product: {name}")

        return product

    def update_price(self, product: Product, store: Supermarket, price: float) -> Price:
        """Update or create price entry"""
        price_entry = (
            self.db.query(Price)
            .filter(Price.product_id == product.id, Price.store_id == store.id)
            .first()
        )

        if price_entry:
            old_price = float(price_entry.price)
            price_entry.price = Decimal(str(price))
            logger.info(f"Updated price for {product.name} at {store.name}: {old_price} -> {price}")
        else:
            price_entry = Price(product_id=product.id, store_id=store.id, price=Decimal(str(price)))
            self.db.add(price_entry)
            logger.info(f"Created price for {product.name} at {store.name}: {price}")

        self.db.commit()
        self.db.refresh(price_entry)
        return price_entry

    async def scrape_mercadona_product(self, query: str) -> List[dict]:
        """
        Scrape Mercadona for a specific product query and update database.
        Returns list of found products with prices.
        """
        results = []

        try:
            # Get or create the Mercadona store entry
            store = self.get_or_create_supermarket(self.STORE_NAME)

            # Search Mercadona
            logger.info(f"Searching Mercadona for: {query}")
            cheapest, matches = await search_mercadona_cheapest(query, max_category_groups=5)

            if not matches:
                logger.warning(f"No products found for query: {query}")
                return []

            # Update database with found products
            for merc_product in matches[:10]:  # Limit to top 10 matches
                product = self.get_or_create_product(
                    name=merc_product.name, category=merc_product.category_name
                )

                self.update_price(product, store, merc_product.price)

                results.append(
                    {
                        "name": merc_product.name,
                        "price": merc_product.price,
                        "category": merc_product.category_name,
                        "subcategory": merc_product.subcategory_name,
                        "store": self.STORE_NAME,
                    }
                )

            logger.info(f"Updated {len(results)} products for query: {query}")

        except Exception as e:
            logger.error(f"Error scraping Mercadona for {query}: {e}")
            raise

        return results

    async def scrape_all_products(self, queries: Optional[List[str]] = None) -> dict:
        """
        Scrape multiple products and update database.
        If no queries provided, uses default common grocery items.
        """
        if queries is None:
            # Default queries - common Spanish grocery items
            queries = [
                "leche",
                "huevos",
                "pan",
                "arroz",
                "pasta",
                "pollo",
                "tomate",
                "patatas",
                "aceite oliva",
                "yogur",
            ]

        all_results = {
            "total_products_updated": 0,
            "queries_processed": 0,
            "errors": [],
            "products": [],
        }

        for query in queries:
            try:
                results = await self.scrape_mercadona_product(query)
                all_results["products"].extend(results)
                all_results["total_products_updated"] += len(results)
                all_results["queries_processed"] += 1
            except Exception as e:
                all_results["errors"].append({"query": query, "error": str(e)})

        return all_results


def run_scraper_sync(db: Session, queries: Optional[List[str]] = None) -> dict:
    """
    Synchronous wrapper for running the scraper.
    Can be called from a scheduled job or API endpoint.
    """
    service = ScraperService(db)
    return asyncio.run(service.scrape_all_products(queries))
