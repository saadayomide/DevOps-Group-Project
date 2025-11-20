import time
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from orm.models import Price, Product, Supermarket
from tests.conftest import PRICE_COUNT, PRODUCT_COUNT, SUPERMARKET_COUNT


def test_prices_table_has_full_matrix(db_session):
    prices = db_session.query(Price).all()
    assert len(prices) == PRICE_COUNT

    for price in prices:
        assert price.price is not None
        assert Decimal(price.price) >= Decimal("0.01")


def test_join_between_tables_returns_expected_rows(db_session):
    join_rows = (
        db_session.query(Product.name, Supermarket.name, Price.price)
        .join(Price, Price.product_id == Product.id)
        .join(Supermarket, Supermarket.id == Price.store_id)
        .all()
    )
    assert len(join_rows) == PRODUCT_COUNT * SUPERMARKET_COUNT


def test_milk_prices_across_stores_returns_three_rows(db_session):
    join_rows = (
        db_session.query(Supermarket.name, Price.price)
        .join(Price, Price.store_id == Supermarket.id)
        .join(Product, Product.id == Price.product_id)
        .filter(Product.name == "milk")
        .order_by(Supermarket.name)
        .all()
    )
    assert len(join_rows) == SUPERMARKET_COUNT
    assert {row[0] for row in join_rows} == {"Walmart", "Target", "Costco"}


def test_foreign_keys_prevent_orphan_prices(db_session):
    orphan = Price(product_id=9999, store_id=9999, price=Decimal("1.00"))
    db_session.add(orphan)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_price_join_executes_under_100ms(db_session):
    start = time.perf_counter()
    db_session.query(Price).join(Product).join(Supermarket).all()
    duration_ms = (time.perf_counter() - start) * 1000
    assert duration_ms < 100
