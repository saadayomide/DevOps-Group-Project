"""Scoring and filtering for candidate offers.

Implements hard filters, scoring heuristics and a filter->score->rank pipeline.
"""

from typing import Dict, List, Optional, Tuple
from app.services.normalization import ProductSpec, normalize_string, CATEGORY_RULES


# Tunable weights
WEIGHTS = {
    "category": 40,
    "brand": 25,
    "variant": 10,
    "token_overlap": 1,
    "price_bonus": 3,
    "irrelevant_penalty": -20,
}


def _safe_price(offer: Dict) -> Optional[float]:
    p = offer.get("price")
    try:
        if p is None:
            return None
        return float(p)
    except Exception:
        return None


def hard_filters_fail(spec: ProductSpec, offer: Dict) -> bool:
    """Return True if this offer should be rejected outright by hard filters."""
    parts = [
        str(offer.get("name") or ""),
        str(offer.get("category") or ""),
        str(offer.get("description") or ""),
    ]
    text = normalize_string(" ".join(parts))

    # Forbidden terms for any matched category should reject the offer.
    # Use the canonical CATEGORY_RULES so we consider category-level forbidden terms
    # even when the spec tokens didn't explicitly include them.
    for cat in spec.matched_rules.keys():
        rules = CATEGORY_RULES.get(cat, {})
        for forb in rules.get("forbidden_terms", []):
            # normalize forbidden token to be safe
            if not forb:
                continue
            if normalize_string(forb) in text:
                return True

    # If the offer explicitly reports a category and spec has matched rules, prefer equality
    if spec.category and offer.get("category"):
        offer_cat = normalize_string(str(offer.get("category")))
        if spec.category.lower().strip() != offer_cat:
            # don't hard-fail here; only fail if offer category is clearly unrelated
            pass

    # If price missing entirely, don't hard fail; just deprioritize later
    return False


def score_offer(spec: ProductSpec, offer: Dict, price_rank_score: float = 0.0) -> Optional[float]:
    """Compute a numeric score for an offer. Return None if rejected."""
    if hard_filters_fail(spec, offer):
        return None

    score = 0.0
    parts = [
        str(offer.get("name") or ""),
        str(offer.get("category") or ""),
        str(offer.get("description") or ""),
    ]
    text = normalize_string(" ".join(parts))
    tokens = set(spec.tokens or [])

    # Category alignment
    if spec.matched_rules:
        # if any matched rule contains base match, give category weight
        for cat, match in spec.matched_rules.items():
            if match.get("matched_base"):
                # if offer declares category and matches, give full; otherwise give smaller
                offer_cat = normalize_string(str(offer.get("category") or ""))
                if offer_cat and cat in offer_cat:
                    score += WEIGHTS["category"]
                else:
                    score += WEIGHTS["category"] * 0.6
                break

    # Brand match
    if spec.brand:
        if spec.brand in text:
            score += WEIGHTS["brand"]

    # Variant match
    for v in spec.variants:
        if v and v in text:
            score += WEIGHTS["variant"]

    # Token overlap
    overlap = len(tokens.intersection(set(text.split())))
    score += overlap * WEIGHTS["token_overlap"]

    # Price rank helps but does not dominate
    score += price_rank_score * WEIGHTS["price_bonus"]

    # Penalize presence of explicit forbidden tokens across all matched categories
    for cat in spec.matched_rules.keys():
        rules = CATEGORY_RULES.get(cat, {})
        for forb in rules.get("forbidden_terms", []):
            if not forb:
                continue
            if normalize_string(forb) in text:
                score += WEIGHTS["irrelevant_penalty"]

    return score


def filter_and_pick_best(
    spec: ProductSpec, offers: List[Dict], top_k: int = 5
) -> Tuple[Optional[Dict], List[Dict]]:
    """Filter offers, score them, rank and return best and top-k list."""
    if not offers:
        return None, []

    # Normalize offers and attach safe price
    normalized_offers = []
    for idx, o in enumerate(offers):
        price = _safe_price(o)
        # ensure minimal shape
        normalized_offers.append({**o, "_orig_index": idx, "_price": price})

    # Apply hard filters
    filtered = [o for o in normalized_offers if not hard_filters_fail(spec, o)]

    if not filtered:
        return None, []

    # Compute price rank score: cheaper offers get higher small bonus
    def price_sort_key(x):
        p = x.get("_price")
        return (p is None, p if p is not None else float("inf"))

    offers_with_price = sorted(filtered, key=price_sort_key)
    price_rank_map = {
        o["_orig_index"]: (len(offers_with_price) - i) / len(offers_with_price)
        for i, o in enumerate(offers_with_price)
    }

    scored = []
    for o in filtered:
        pr_score = price_rank_map.get(o.get("_orig_index"), 0.0)
        s = score_offer(spec, o, price_rank_score=pr_score)
        if s is not None:
            scored.append((s, o))

    if not scored:
        return None, []

    # Sort by score desc, then price asc (None prices last)
    def sort_key(t):
        p = t[1].get("_price")
        return (-t[0], p if p is not None else float("inf"))

    scored.sort(key=sort_key)
    ranked = [o for _, o in scored]

    best = ranked[0] if ranked else None
    return best, ranked[:top_k]
