"""
Unit tests for matcher_service facade
"""

from app.services.matcher_service import (
    match_best_offer,
    build_and_match,
    explain_match,
    MatchResult,
)
from app.services.normalization import build_product_spec


def make_offer(name, price=None, category=None, description=None, store="TestStore"):
    return {
        "name": name,
        "price": price,
        "category": category,
        "description": description or "",
        "store": store,
        "url": f"http://test/{name.replace(' ', '-')}",
    }


class TestMatchBestOffer:
    """Tests for match_best_offer function"""

    def test_returns_match_result(self):
        spec = build_product_spec("Leche 1L", category="milk")
        offers = [
            make_offer("Leche entera 1L", price=1.0, category="milk"),
            make_offer("Leche desnatada 1L", price=1.2, category="milk"),
        ]

        result = match_best_offer(spec, offers)

        assert isinstance(result, MatchResult)
        assert result.offers_scanned == 2
        assert result.best_offer is not None
        assert result.spec_summary is not None

    def test_empty_offers_returns_no_match(self):
        spec = build_product_spec("Leche 1L")
        result = match_best_offer(spec, [])

        assert result.best_offer is None
        assert result.filtered_offers == []
        assert result.offers_scanned == 0

    def test_forbidden_terms_filter_out_offers(self):
        spec = build_product_spec("Leche 1L", category="milk")
        offers = [
            make_offer("Milk powder instant", price=0.5, category="milk"),  # forbidden: "powder"
            make_offer(
                "Batido de chocolate", price=0.8, category="milk"
            ),  # forbidden: "chocolate", "batido"
            make_offer("Leche entera 1L", price=1.0, category="milk"),  # valid
        ]

        result = match_best_offer(spec, offers)

        # Should pick the valid milk option
        assert result.best_offer is not None
        assert "entera" in result.best_offer["name"].lower()


class TestBuildAndMatch:
    """Tests for build_and_match convenience function"""

    def test_builds_spec_and_matches(self):
        offers = [
            make_offer("Hacendado Leche desnatada 1L", price=0.89, category="milk"),
            make_offer("Puleva Leche entera 1L", price=1.10, category="milk"),
        ]

        result = build_and_match(
            name="Leche 1L",
            offers=offers,
            brand="hacendado",
            category="milk",
            variants=["desnatada"],
        )

        assert result.best_offer is not None
        # Brand + variant match should prefer Hacendado desnatada
        assert "hacendado" in result.best_offer["name"].lower()

    def test_variant_preference(self):
        offers = [
            make_offer("Leche entera 1L", price=0.80, category="milk"),
            make_offer("Leche desnatada sin lactosa 1L", price=1.20, category="milk"),
        ]

        result = build_and_match(name="Leche", offers=offers, variants=["desnatada", "sin lactosa"])

        # Despite being more expensive, variant match should boost the desnatada option
        assert result.best_offer is not None
        assert "desnatada" in result.best_offer["name"].lower()


class TestExplainMatch:
    """Tests for explain_match function"""

    def test_explains_valid_offer(self):
        spec = build_product_spec("Leche 1L", brand="hacendado")
        offer = make_offer("Hacendado Leche entera 1L", price=1.0, category="milk")

        explanation = explain_match(spec, offer)

        assert explanation["rejected"] is False
        assert explanation["score"] is not None
        assert explanation["spec_brand"] == "hacendado"

    def test_explains_rejected_offer(self):
        spec = build_product_spec("Leche 1L", category="milk")
        offer = make_offer("Milk powder instant formula", price=0.5, category="milk")

        explanation = explain_match(spec, offer)

        # "powder" should cause rejection
        assert explanation["rejected"] is True
        assert explanation["score"] is None


class TestMatchResultToDict:
    """Tests for MatchResult.to_dict method"""

    def test_to_dict_structure(self):
        spec = build_product_spec("Test")
        result = match_best_offer(spec, [make_offer("Test Product", price=1.0)])

        d = result.to_dict()

        assert "best_offer" in d
        assert "filtered_offers" in d
        assert "spec_summary" in d
        assert "offers_scanned" in d
        assert "offers_passed_filter" in d
