from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from orm.models import Base, Price, Product, Supermarket

PRODUCTS: List[Dict[str, str]] = [
    {"name": "milk", "category": "Dairy"},
    {"name": "eggs", "category": "Dairy"},
    {"name": "rice", "category": "Pantry"},
    {"name": "pasta", "category": "Pantry"},
    {"name": "chicken breast", "category": "Meat"},
    {"name": "apples", "category": "Produce"},
    {"name": "bread", "category": "Bakery"},
    {"name": "cereal", "category": "Breakfast"},
    {"name": "cheese", "category": "Dairy"},
    {"name": "ground beef", "category": "Meat"},
]

SUPERMARKETS: List[Dict[str, str]] = [
    {"name": "Walmart", "city": "Bentonville"},
    {"name": "Target", "city": "Minneapolis"},
    {"name": "Costco", "city": "Issaquah"},
]

PRICES: List[Tuple[str, str, Decimal]] = [
    ("milk", "Walmart", Decimal("1.94")),
    ("milk", "Target", Decimal("2.15")),
    ("milk", "Costco", Decimal("1.99")),
    ("eggs", "Walmart", Decimal("2.59")),
    ("eggs", "Target", Decimal("2.79")),
    ("eggs", "Costco", Decimal("2.69")),
    ("rice", "Walmart", Decimal("5.39")),
    ("rice", "Target", Decimal("5.19")),
    ("rice", "Costco", Decimal("4.99")),
    ("pasta", "Walmart", Decimal("1.49")),
    ("pasta", "Target", Decimal("1.69")),
    ("pasta", "Costco", Decimal("1.39")),
    ("chicken breast", "Walmart", Decimal("8.49")),
    ("chicken breast", "Target", Decimal("8.99")),
    ("chicken breast", "Costco", Decimal("8.19")),
    ("apples", "Walmart", Decimal("3.19")),
    ("apples", "Target", Decimal("3.39")),
    ("apples", "Costco", Decimal("3.09")),
    ("bread", "Walmart", Decimal("2.49")),
    ("bread", "Target", Decimal("2.69")),
    ("bread", "Costco", Decimal("2.19")),
    ("cereal", "Walmart", Decimal("4.39")),
    ("cereal", "Target", Decimal("4.69")),
    ("cereal", "Costco", Decimal("4.19")),
    ("cheese", "Walmart", Decimal("5.59")),
    ("cheese", "Target", Decimal("5.89")),
    ("cheese", "Costco", Decimal("5.39")),
    ("ground beef", "Walmart", Decimal("7.99")),
    ("ground beef", "Target", Decimal("8.29")),
    ("ground beef", "Costco", Decimal("7.79")),
]

PRODUCT_COUNT = len(PRODUCTS)
SUPERMARKET_COUNT = len(SUPERMARKETS)
PRICE_COUNT = len(PRICES)


def seed_data(session: Session) -> None:
    product_ids: Dict[str, int] = {}
    store_ids: Dict[str, int] = {}

    for product in PRODUCTS:
        product_row = Product(name=product["name"], category=product.get("category"))
        session.add(product_row)
        session.flush()
        product_ids[product_row.name] = product_row.id

    for store in SUPERMARKETS:
        store_row = Supermarket(name=store["name"], city=store["city"])
        session.add(store_row)
        session.flush()
        store_ids[store_row.name] = store_row.id

    for product_name, store_name, price in PRICES:
        session.add(
            Price(
                product_id=product_ids[product_name],
                store_id=store_ids[store_name],
                price=price,
            )
        )

    session.commit()


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    session.execute(text("PRAGMA foreign_keys=ON"))
    seed_data(session)

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
