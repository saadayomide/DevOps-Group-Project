from app.services.matching.spec import ProductSpec
from app.services.matching.scorer import filter_and_pick_best
from app.services.scrapers.base import Offer


def test_milk_scoring_filters_obvious_false_positives():
    spec = ProductSpec(
        category_code="milk",
        category_label="Leche",
        brand=None,
        variants=["desnatada"],
        quantity=1.0,
        unit="L",
    )

    offers = [
        Offer(store="mercadona", name="Leche UHT desnatada Hacendado 1L", brand="Hacendado", price=0.8, url=None),
        Offer(store="mercadona", name="Leche facial limpiadora 200ml", brand=None, price=2.5, url=None),
        Offer(store="mercadona", name="Cafe con leche cappuccino 250ml", brand=None, price=1.2, url=None),
        Offer(store="alcampo", name="Leche desnatada sin lactosa 1L", brand=None, price=0.9, url=None),
    ]

    best, filtered = filter_and_pick_best(spec, offers)

    names = [o.name for o in filtered]
    assert "Leche facial limpiadora 200ml" not in names
    assert "Cafe con leche cappuccino 250ml" not in names
    assert best is not None
    assert best.name in {
        "Leche UHT desnatada Hacendado 1L",
        "Leche desnatada sin lactosa 1L",
    }
