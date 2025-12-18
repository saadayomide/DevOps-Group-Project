"""Service to refresh a shopping list: query scrapers, match offers, update DB."""

import asyncio
from datetime import datetime, timezone
import logging
import os
from typing import List
from sqlalchemy.orm import Session
from app.services.normalization import build_product_spec, summarize_spec
from app.services.scorer import filter_and_pick_best
from app.services.scraper_service import ScraperService
from app.models import ShoppingList
from app.services import metrics

logger = logging.getLogger(__name__)


def _make_query_from_spec(spec) -> str:
    parts = [spec.name]
    if spec.brand:
        parts.insert(0, spec.brand)
    if spec.variants:
        parts.extend(spec.variants)
    return " ".join([p for p in parts if p])


async def async_refresh_shopping_list(list_id: int, db: Session) -> dict:
    """Async implementation of the refresh flow.

    This can be awaited from async endpoints or scheduled as a background task.
    """
    sl: ShoppingList = db.get(ShoppingList, list_id)
    if not sl:
        raise ValueError(f"ShoppingList {list_id} not found")

    summary = {"list_id": list_id, "updated_items": 0, "errors": []}

    for item in sl.items:
        try:
            variants = (item.variants or "").split(",") if item.variants else None
            spec = build_product_spec(
                item.name, brand=item.brand, category=item.category, variants=variants
            )
            query = _make_query_from_spec(spec)

            # Call scrapers with retry/backoff; if scraper fails after retries, continue
            offers: List[dict] = []
            max_retries = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
            backoff = float(os.getenv("SCRAPER_BACKOFF_SECONDS", "0.5"))
            attempt = 0
            while attempt <= max_retries:
                try:
                    scraper = ScraperService(db)
                    # ScraperManager.get_offers is sync; run in executor
                    loop = asyncio.get_running_loop()
                    func = scraper.manager.get_offers
                    offers = await loop.run_in_executor(None, func, query) or []
                    break
                except Exception as e:
                    attempt += 1
                    logger.warning(
                        "Scraper error (attempt %s/%s) for query=%s: %s",
                        attempt,
                        max_retries,
                        query,
                        e,
                    )
                    if attempt > max_retries:
                        logger.exception(
                            "Scraper failed after %s attempts for query=%s", max_retries, query
                        )
                        metrics.REFRESH_ERRORS_TOTAL.inc()
                        offers = []
                        break
                    await asyncio.sleep(backoff * attempt)

            # Convert offers to expected structure (name, price, category, etc.)
            normalized_offers = []
            for o in offers:
                # Support Offer objects from ScraperManager or plain dicts
                if hasattr(o, "to_dict"):
                    od = o.to_dict()
                elif isinstance(o, dict):
                    od = o
                else:
                    # Fallback: build dict from attributes
                    cat = getattr(o, "category", None) or getattr(o, "category_name", None)
                    desc = (
                        getattr(o, "subcategory", None)
                        or getattr(o, "description", None)
                        or getattr(o, "subcategory_name", "")
                    )
                    od = {
                        "name": getattr(o, "name", None),
                        "price": getattr(o, "price", None),
                        "category": cat,
                        "description": desc,
                        "store": getattr(o, "store", ""),
                        "url": getattr(o, "url", None) or getattr(o, "link", None),
                    }

                normalized_offers.append(
                    {
                        "name": od.get("name"),
                        "price": od.get("price"),
                        "category": od.get("category"),
                        "description": od.get("subcategory") or od.get("description") or "",
                        "store": od.get("store") or "",
                        "url": od.get("url") or od.get("link") or None,
                    }
                )

            metrics.OFFERS_SCANNED_TOTAL.inc(len(normalized_offers))

            best, ranked = filter_and_pick_best(spec, normalized_offers, top_k=10)

            comparison = {
                "query": query,
                "offers_count": len(normalized_offers),
                "ranked": [
                    {
                        "name": r.get("name"),
                        "store": r.get("store"),
                        "price": r.get("_price"),
                        "url": r.get("url"),
                    }
                    for r in ranked
                ],
                "selected": None,
                "spec": summarize_spec(spec),
            }

            if best:
                item.best_store = best.get("store")
                item.best_price = best.get("_price")
                item.best_url = best.get("url")
                comparison["selected"] = {
                    "name": best.get("name"),
                    "store": best.get("store"),
                    "price": best.get("_price"),
                    "url": best.get("url"),
                }
                metrics.BEST_SELECTED_TOTAL.inc()
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

    sl.last_refreshed = datetime.now(timezone.utc)
    db.add(sl)
    db.commit()
    summary["last_refreshed"] = sl.last_refreshed.isoformat()

    return summary


def refresh_shopping_list(list_id: int, db: Session) -> dict:
    """Synchronous wrapper kept for backwards compatibility."""
    return asyncio.run(async_refresh_shopping_list(list_id, db))
