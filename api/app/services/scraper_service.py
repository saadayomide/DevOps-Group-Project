"""
Scraper service to orchestrate price scraping and database updates.

This service connects the scraper layer with the database layer.
Uses ScraperManager facade to fetch from all stores.

Architecture:
- API routes → ScraperService → ScraperManager → Individual Scrapers → DB

SOLID Principles:
- SRP: This service handles only DB integration
- DIP: Depends on ScraperManager abstraction
"""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Product, Supermarket, Price
from app.services.scrapers import ScraperManager, Offer

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Service to orchestrate scraping and database updates.

    Responsibilities:
    - Coordinate scraping across stores
    - Update database with scraped prices
    - Handle errors gracefully
    """

    def __init__(self, db: Session):
        self.db = db
        self.manager = ScraperManager()

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

    def get_or_create_product(self, name: str, category: str = "General") -> Product:
        """Get existing product or create new one"""
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
            price_entry = Price(
                product_id=product.id,
                store_id=store.id,
                price=Decimal(str(price)),
            )
            self.db.add(price_entry)
            logger.info(f"Created price for {product.name} at {store.name}: {price}")

        self.db.commit()
        self.db.refresh(price_entry)
        return price_entry

    def process_offers(self, offers: List[Offer]) -> Dict[str, Any]:
        """
        Process a list of offers and update the database.

        Args:
            offers: List of Offer objects from scrapers

        Returns:
            Summary of processed offers
        """
        results = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "errors": [],
        }

        for offer in offers:
            try:
                # Get or create store
                store = self.get_or_create_supermarket(offer.store)

                # Get or create product
                product = self.get_or_create_product(offer.name)

                # Check if this is an update or create
                existing = (
                    self.db.query(Price)
                    .filter(Price.product_id == product.id, Price.store_id == store.id)
                    .first()
                )

                if existing:
                    results["updated"] += 1
                else:
                    results["created"] += 1

                # Update price
                self.update_price(product, store, offer.price)
                results["processed"] += 1

            except Exception as e:
                results["errors"].append(
                    {
                        "offer": offer.name,
                        "store": offer.store,
                        "error": str(e),
                    }
                )
                logger.error(f"Error processing offer {offer.name}: {e}")

        return results

    async def scrape_product(self, query: str, store: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape products for a query and update database.

        Args:
            query: Search query
            store: Optional specific store to scrape

        Returns:
            Dictionary with results summary
        """
        logger.info(f"Scraping for query: {query}, store: {store or 'all'}")

        try:
            # Get offers from scraper(s)
            if store:
                offers = self.manager.get_offers_by_store(query, store)
            else:
                offers = self.manager.get_offers(query)

            if not offers:
                return {
                    "status": "no_results",
                    "message": f"No products found for: {query}",
                    "query": query,
                    "store": store,
                    "offers_found": 0,
                    "processed": 0,
                }

            # Process offers into database
            results = self.process_offers(offers)

            return {
                "status": "success",
                "message": f"Processed {results['processed']} products",
                "query": query,
                "store": store,
                "offers_found": len(offers),
                **results,
            }

        except Exception as e:
            logger.error(f"Error scraping for {query}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "query": query,
                "store": store,
                "offers_found": 0,
                "processed": 0,
            }

    async def scrape_all_products(self, queries: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape multiple products and update database.

        Args:
            queries: List of search queries (default: common grocery items)

        Returns:
            Aggregated results from all queries
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
                "aceite",
                "yogur",
            ]

        all_results = {
            "status": "completed",
            "total_offers_found": 0,
            "total_processed": 0,
            "total_created": 0,
            "total_updated": 0,
            "queries_processed": 0,
            "errors": [],
            "details": [],
        }

        for query in queries:
            try:
                result = await self.scrape_product(query)
                all_results["details"].append(result)
                all_results["total_offers_found"] += result.get("offers_found", 0)
                all_results["total_processed"] += result.get("processed", 0)
                all_results["total_created"] += result.get("created", 0)
                all_results["total_updated"] += result.get("updated", 0)
                all_results["queries_processed"] += 1

                if result.get("errors"):
                    all_results["errors"].extend(result["errors"])

            except Exception as e:
                all_results["errors"].append(
                    {
                        "query": query,
                        "error": str(e),
                    }
                )

        return all_results


def run_scraper_sync(db: Session, queries: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for running the scraper.
    Can be called from a scheduled job or API endpoint.
    """
    import asyncio

    service = ScraperService(db)
    return asyncio.run(service.scrape_all_products(queries))
