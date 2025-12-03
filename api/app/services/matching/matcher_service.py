from typing import List, Tuple, Optional
from .spec import ProductSpec
from .scorer import filter_and_pick_best
from app.services.scrapers.base import Offer


async def find_best_offer_for_item(
    spec: ProductSpec,
    offers: List[Offer],
) -> Tuple[Optional[Offer], List[Offer]]:
    """
    Given a ProductSpec and a list of Offer objects (from ALL scrapers),
    return (best_offer, filtered_offers).
    """
    return filter_and_pick_best(spec, offers)
