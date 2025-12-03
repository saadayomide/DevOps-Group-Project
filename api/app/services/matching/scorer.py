from typing import List, Tuple, Optional
from .spec import ProductSpec
from .filters import get_category_rules, STOPWORDS
from .normalize import normalize
from app.services.scrapers.base import Offer


def score_offer(spec: ProductSpec, offer: Offer) -> float:
    name_norm = normalize(offer.name)
    tokens = set(name_norm.split())

    rules = get_category_rules(spec.category_code)
    base_terms = set(rules.get("base_terms", []))
    forbidden_terms = set(rules.get("forbidden_terms", []))

    # HARD RULE 1: must contain at least one base term (if defined)
    if base_terms and not (base_terms & tokens):
        return -1e9  # kill

    # HARD RULE 2: forbidden terms → kill
    if forbidden_terms and (forbidden_terms & tokens):
        return -1e9  # kill

    score = 0.0

    # Variants
    variant_tokens = set()
    for v in spec.variants:
        variant_tokens |= set(normalize(v).split())
    score += 2.0 * len(variant_tokens & tokens)

    # Brand
    if spec.brand:
        brand_tokens = set(normalize(spec.brand).split())
        if brand_tokens & tokens:
            score += 3.0
        else:
            score -= 2.0

    # Category label
    cat_tokens = set(normalize(spec.category_label).split())
    score += 1.5 * len(cat_tokens & tokens)

    # Penalty for extra tokens (noise)
    relevant = variant_tokens | cat_tokens
    extra_tokens = tokens - relevant - STOPWORDS
    score -= 0.1 * len(extra_tokens)

    return score


def filter_and_pick_best(spec: ProductSpec, offers: List[Offer]) -> Tuple[Optional[Offer], List[Offer]]:
    """
    Returns (best_offer, filtered_offers).
    best_offer may be None if no offer passes filters.
    filtered_offers contains only offers that passed the hard rules.
    """
    scored: List[Tuple[float, Offer]] = []
    for o in offers:
        s = score_offer(spec, o)
        if s > -1e8:
            scored.append((s, o))

    if not scored:
        return None, []

    # Sort: first by price (ascending), then by score (descending)
    scored.sort(key=lambda t: (t[1].price, -t[0]))

    best_offer = scored[0][1]
    filtered_offers = [o for (_, o) in scored]
    return best_offer, filtered_offers
