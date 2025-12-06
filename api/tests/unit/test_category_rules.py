"""
Unit tests for category rules and ProductSpec builder
"""

from app.services.normalization import (
    CATEGORY_RULES,
    build_product_spec,
    normalize_string,
)


def test_category_rules_loaded():
    assert isinstance(CATEGORY_RULES, dict)
    # basic categories present
    assert "milk" in CATEGORY_RULES
    assert "eggs" in CATEGORY_RULES
    assert "bread" in CATEGORY_RULES


def test_build_product_spec_matches_milk_and_variant():
    spec = build_product_spec("Leche desnatada 1L", brand="LaMarca", variants=["desnatada"]) 
    # tokens should include normalized words
    assert "leche" in spec.tokens or "milk" in spec.tokens
    # variant normalized present
    assert "desnatada" in spec.variants
    # matched rules should include milk category
    assert "milk" in spec.matched_rules


def test_build_product_spec_forbidden_term_detected():
    spec = build_product_spec("Milk powder instant", brand=None)
    # powder is a forbidden term for milk
    matches = spec.matched_rules.get("milk")
    # when powder appears, matched_forbidden should include it
    if matches:
        assert "powder" in matches.get("matched_forbidden", [])
