from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.models import ShoppingList, ShoppingListItem
from app.config import settings
from app.services.matching.spec import from_shopping_item, ProductSpec
from app.services.matching.matcher_service import find_best_offer_for_item
from app.services.scrapers import mercadona, carrefour, alcampo
from app.services.scrapers.base import Offer


async def refresh_shopping_list(db: Session, shopping_list: ShoppingList) -> ShoppingList:
    """
    Refresh a shopping list: fetch offers, pick best per item, update fields.
    In test environment, skip external calls to keep tests fast and deterministic.
    """
    # Skip external scraping in test environment
    if settings.app_env == "test":
        shopping_list.last_refreshed = datetime.utcnow()
        db.commit()
        db.refresh(shopping_list)
        db.refresh(shopping_list, attribute_names=["items"])
        return shopping_list

    for item in shopping_list.items:
        await _refresh_item(db, item)

    shopping_list.last_refreshed = datetime.utcnow()
    db.commit()
    db.refresh(shopping_list)
    db.refresh(shopping_list, attribute_names=["items"])
    return shopping_list


async def _refresh_item(db: Session, item: ShoppingListItem) -> None:
    """Refresh a single shopping list item by scraping and matching."""
    spec: ProductSpec = from_shopping_item(item)

    # Build query string from spec components
    query_parts = [spec.category_label]
    if spec.brand:
        query_parts.append(spec.brand)
    query_parts.extend(spec.variants)
    query_str = " ".join(query_parts)

    offers: List[Offer] = []

    # Collect offers from available scrapers; keep short list for now to limit latency
    try:
        offers.extend(await mercadona.search_item(query_str))
    except Exception as exc:  # pragma: no cover - defensive
        import logging
        logging.exception("Mercadona scraper failed: %s", exc)

    try:
        offers.extend(await carrefour.search_item(query_str))
    except Exception:
        pass

    try:
        offers.extend(await alcampo.search_item(query_str))
    except Exception:
        pass

    best_offer, filtered_offers = await find_best_offer_for_item(spec, offers)

    item.best_store = best_offer.store if best_offer else None
    item.best_price = best_offer.price if best_offer else None
    item.best_url = best_offer.url if best_offer else None
    item.comparison_json = {"offers": [o.dict() for o in filtered_offers]}

    db.add(item)
