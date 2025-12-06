"""Service to refresh a shopping list: query scrapers, match offers, and update DB."""
import asyncio
import json
import datetime
import logging
from typing import List
from sqlalchemy.orm import Session
from app.services.normalization import build_product_spec, summarize_spec
from app.services.scorer import filter_and_pick_best
from app.services.scraper_service import ScraperService
from app.models import ShoppingList, ShoppingListItem

logger = logging.getLogger(__name__)


def _make_query_from_spec(spec) -> str:
    parts = [spec.name]
    if spec.brand:
        parts.insert(0, spec.brand)
    if spec.variants:
        parts.extend(spec.variants)
    return " ".join([p for p in parts if p])


def refresh_shopping_list(list_id: int, db: Session) -> dict:
    """Refresh a shopping list by id.

    For each item:
      - build ProductSpec
      - call available scrapers for a query (currently Mercadona)
      - apply matching engine -> best and ranked
      - update ShoppingListItem.best_* and comparison_json

    Returns a summary dict.
    """
    sl: ShoppingList = db.query(ShoppingList).get(list_id)
    if not sl:
        raise ValueError(f"ShoppingList {list_id} not found")

    summary = {"list_id": list_id, "updated_items": 0, "errors": []}

    for item in sl.items:
        try:
            spec = build_product_spec(item.name, brand=item.brand, category=item.category, variants=(item.variants or "").split(",") if item.variants else None)
            query = _make_query_from_spec(spec)

            # Call scrapers safely; if one scraper fails, continue
            offers: List[dict] = []
            try:
                scraper = ScraperService(db)
                # use asyncio.run to call the async scraper method
                offers = asyncio.run(scraper.scrape_mercadona_product(query)) or []
            except Exception as e:
                logger.warning(f"Scraper error for query={query}: {e}")
                offers = []

            # Convert offers to expected structure (ensure keys name, price, category, description, store, url)
            normalized_offers = []
            for o in offers:
                normalized_offers.append(
                    {
                        "name": o.get("name"),
                        "price": o.get("price"),
                        "category": o.get("category"),
                        "description": o.get("subcategory") or o.get("description") or "",
                        "store": o.get("store") or "",
                        "url": o.get("url") or o.get("link") or None,
                    }
                )

            best, ranked = filter_and_pick_best(spec, normalized_offers, top_k=10)

            comparison = {
                "query": query,
                "offers_count": len(normalized_offers),
                "ranked": [
                    {"name": r.get("name"), "store": r.get("store"), "price": r.get("_price"), "url": r.get("url")} for r in ranked
                ],
                "selected": None,
                "spec": summarize_spec(spec),
            }

            if best:
                item.best_store = best.get("store")
                item.best_price = best.get("_price")
                item.best_url = best.get("url")
                comparison["selected"] = {"name": best.get("name"), "store": best.get("store"), "price": best.get("_price"), "url": best.get("url")}
            else:
                item.best_store = None
                item.best_price = None
                item.best_url = None

            item.comparison_json = comparison
            db.add(item)
            db.commit()
            db.refresh(item)

            summary["updated_items"] += 1

        except Exception as e:
            logger.exception("Error refreshing item %s: %s", item.id, e)
            summary["errors"].append({"item_id": item.id, "error": str(e)})

    sl.last_refreshed = datetime.datetime.utcnow()
    db.add(sl)
    db.commit()
    summary["last_refreshed"] = sl.last_refreshed.isoformat()

    return summary
