from orm.models import get_all_products, get_all_supermarkets, get_prices_for
from tests.conftest import PRICE_COUNT, PRODUCT_COUNT, SUPERMARKET_COUNT


def test_get_all_products_returns_sorted_list(db_session):
    products = get_all_products(db_session)
    assert len(products) == PRODUCT_COUNT
    names = [product.name for product in products]
    assert names == sorted(names)


def test_get_all_supermarkets_returns_sorted_list(db_session):
    supermarkets = get_all_supermarkets(db_session)
    assert len(supermarkets) == SUPERMARKET_COUNT
    names = [store.name for store in supermarkets]
    assert names == sorted(names)


def test_get_prices_for_filters_by_product_and_store(db_session):
    all_prices = get_prices_for(db_session)
    assert len(all_prices) == PRICE_COUNT

    milk = [price for price in all_prices if price.product_id == all_prices[0].product_id]
    filtered = get_prices_for(db_session, product_ids=[all_prices[0].product_id])
    assert {price.id for price in filtered} == {price.id for price in milk}

    # Combined filter
    first_store_id = filtered[0].store_id
    single_store_prices = get_prices_for(
        db_session,
        product_ids=[filtered[0].product_id],
        store_ids=[first_store_id],
    )
    assert len(single_store_prices) == 1
