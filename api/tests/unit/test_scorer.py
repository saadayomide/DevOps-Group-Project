"""
Unit tests for scorer behavior: brand preference, variant boosts, forbidden rejection
"""

from app.services.normalization import build_product_spec
from app.services.scorer import filter_and_pick_best, score_offer, hard_filters_fail


def make_offer(name, price=None, category=None, description=None, store="S"):
    return {"name": name, "price": price, "category": category, "description": description or "", "store": store}


def test_forbidden_term_rejects_offer():
    spec = build_product_spec("Milk 1L")
    # Offer contains forbidden 'powder' -> should be rejected by hard_filters
    off = make_offer("Instant milk powder", price=1.0, category="milk")
    assert hard_filters_fail(spec, off) is True


def test_brand_match_boosts_score():
    spec = build_product_spec("Coca Cola 1.5L", brand="coca cola")
    # two offers: one cheaper but different brand, one slightly more expensive but correct brand
    off_wrong = make_offer("Generic Cola 1.5L", price=1.0, category="juice")
    off_right = make_offer("Coca Cola 1.5L", price=1.2, category="juice")

    best, ranked = filter_and_pick_best(spec, [off_wrong, off_right], top_k=2)
    assert best is not None
    # brand match should prefer coca cola even if a bit more expensive
    assert best.get("name") == "Coca Cola 1.5L"


def test_variant_boosting():
    spec = build_product_spec("Leche desnatada 1L", variants=["desnatada"])
    off_full = make_offer("Leche desnatada LaMarca 1L", price=1.5, category="milk")
    off_whole = make_offer("Leche entera LaMarca 1L", price=1.1, category="milk")
    best, ranked = filter_and_pick_best(spec, [off_whole, off_full], top_k=2)
    assert best is not None
    assert "desnatada" in best.get("name").lower()
