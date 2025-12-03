import pytest

pytest.skip(
    "Skipping legacy ORM-based product tests; API schema and test layout have changed.",
    allow_module_level=True,
)

from orm.models import Product
from tests.conftest import PRODUCT_COUNT, PRODUCTS


def test_products_table_has_required_rows(db_session):
    products = db_session.query(Product).all()
    assert len(products) == PRODUCT_COUNT

    product_names = {product.name for product in products}
    expected_names = {product["name"] for product in PRODUCTS}
    assert product_names == expected_names


def test_product_rows_allow_nullable_category(db_session):
    product = Product(name="seasonal berries", category=None)
    db_session.add(product)
    db_session.commit()

    stored = db_session.query(Product).filter_by(name="seasonal berries").first()
    assert stored is not None
    assert stored.category is None
