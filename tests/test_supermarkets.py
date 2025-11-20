from sqlalchemy.exc import IntegrityError

from orm.models import Supermarket
from tests.conftest import SUPERMARKET_COUNT, SUPERMARKETS


def test_supermarkets_table_has_expected_rows(db_session):
    supermarkets = db_session.query(Supermarket).order_by(Supermarket.name).all()
    assert len(supermarkets) == SUPERMARKET_COUNT

    for row, expected in zip(supermarkets, sorted(SUPERMARKETS, key=lambda s: s["name"])):
        assert row.name == expected["name"]
        assert row.city == expected["city"]


def test_supermarket_name_city_unique_constraint(db_session):
    duplicate = Supermarket(name="Walmart", city="Bentonville")
    db_session.add(duplicate)

    try:
        db_session.commit()
        raise AssertionError("Expected IntegrityError for duplicate name/city")
    except IntegrityError:
        db_session.rollback()
