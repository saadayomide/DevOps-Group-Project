"""
Matcher Service - Clean facade for the matching engine.

Provides a simple interface for matching product specs against offers.
This service orchestrates normalization, filtering, and scoring.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from app.services.normalization import build_product_spec, summarize_spec, ProductSpec
from app.services.scorer import filter_and_pick_best


@dataclass
class MatchResult:
    """Result of matching a product spec against offers."""

    best_offer: Optional[Dict[str, Any]]
    filtered_offers: List[Dict[str, Any]]
    spec_summary: Dict[str, Any]
    offers_scanned: int
    offers_passed_filter: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "best_offer": self.best_offer,
            "filtered_offers": self.filtered_offers,
            "spec_summary": self.spec_summary,
            "offers_scanned": self.offers_scanned,
            "offers_passed_filter": self.offers_passed_filter,
        }


def match_best_offer(
    spec: ProductSpec, offers: List[Dict[str, Any]], top_k: int = 10
) -> MatchResult:
    """
    Match a product specification against a list of offers.

    This is the main entry point for the matching engine.

    Args:
        spec: ProductSpec built from user input (category, brand, variants, etc.)
        offers: List of offer dictionaries from scrapers
        top_k: Maximum number of ranked offers to return

    Returns:
        MatchResult containing the best offer and ranked alternatives
    """
    best, ranked = filter_and_pick_best(spec, offers, top_k=top_k)

    return MatchResult(
        best_offer=_clean_offer(best) if best else None,
        filtered_offers=[_clean_offer(o) for o in ranked],
        spec_summary=summarize_spec(spec),
        offers_scanned=len(offers),
        offers_passed_filter=len(ranked),
    )


def build_and_match(
    name: str,
    offers: List[Dict[str, Any]],
    brand: Optional[str] = None,
    category: Optional[str] = None,
    variants: Optional[List[str]] = None,
    top_k: int = 10,
) -> MatchResult:
    """
    Convenience function that builds a spec and matches in one call.

    Args:
        name: Product name or search query
        offers: List of offer dictionaries
        brand: Optional brand preference
        category: Optional category hint
        variants: Optional list of variant keywords (e.g., ["desnatada", "sin lactosa"])
        top_k: Maximum number of ranked offers to return

    Returns:
        MatchResult containing the best offer and ranked alternatives
    """
    spec = build_product_spec(name, brand=brand, category=category, variants=variants)
    return match_best_offer(spec, offers, top_k=top_k)


def _clean_offer(offer: Dict[str, Any]) -> Dict[str, Any]:
    """Remove internal keys from offer dict for external consumption."""
    if not offer:
        return {}
    return {
        "name": offer.get("name"),
        "price": offer.get("_price") or offer.get("price"),
        "store": offer.get("store"),
        "category": offer.get("category"),
        "url": offer.get("url"),
    }


def explain_match(spec: ProductSpec, offer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed scoring breakdown for a single offer.

    Useful for debugging and understanding why an offer was ranked a certain way.

    Args:
        spec: ProductSpec to match against
        offer: Single offer dictionary

    Returns:
        Dictionary with score and breakdown details
    """
    from app.services.scorer import hard_filters_fail, score_offer as _score

    rejected = hard_filters_fail(spec, offer)
    if rejected:
        return {
            "offer": offer.get("name"),
            "rejected": True,
            "reason": "Failed hard filters (forbidden terms or category mismatch)",
            "score": None,
        }

    score = _score(spec, offer, price_rank_score=0.5)  # neutral price rank for explanation
    return {
        "offer": offer.get("name"),
        "rejected": False,
        "score": score,
        "spec_tokens": spec.tokens,
        "spec_brand": spec.brand,
        "spec_variants": spec.variants,
        "matched_rules": spec.matched_rules,
    }


__all__ = [
    "MatchResult",
    "match_best_offer",
    "build_and_match",
    "explain_match",
]
