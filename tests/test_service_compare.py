from service import compare_items, SAMPLE_PRICES
from models import CompareRequest

def test_compare_items_basic():
    req = CompareRequest(items=["milk", "bread"])
    resp = compare_items(req, prices=SAMPLE_PRICES)
    assert resp.total_cost == round(sum(r.price for r in resp.recommendations), 2)
    # cheapest milk = Lidl (0.95), cheapest bread = Carrefour (0.75)
    prices = {r.product.lower(): r.price for r in resp.recommendations}
    assert round(prices["milk"], 2) == 0.95
    assert round(prices["bread"], 2) == 0.75

def test_compare_items_missing_item():
    req = CompareRequest(items=["nonexistent"])
    resp = compare_items(req, prices=SAMPLE_PRICES)
    assert len(resp.recommendations) == 1
    assert resp.recommendations[0].cheapest_store in ("N/A",) or resp.recommendations[0].price == 0.0

def test_compare_items_store_filter():
    # restrict to Mercadona and Carrefour
    req = CompareRequest(items=["milk", "eggs"], stores=["Mercadona","Carrefour"])
    resp = compare_items(req, prices=SAMPLE_PRICES)
    # ensure no recommendation points to Lidl
    for r in resp.recommendations:
        assert r.cheapest_store in ("Mercadona","Carrefour")
