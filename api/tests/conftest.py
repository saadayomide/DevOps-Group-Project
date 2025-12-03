"""
Pytest configuration and fixtures for testing (file-based SQLite DB)

This conftest creates a temporary SQLite file DB for tests and provides
fixtures compatible with the project's tests (`test_db`, `test_client`,
`seed_test_data`). It sets `APP_ENV=test` and `SQL_CONNECTION_STRING`
before importing the app so the app uses the test DB and skips migrations.
"""
import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment BEFORE importing app modules
TEST_DB_FILE = os.path.join(tempfile.gettempdir(), "shopsmart_test_db.sqlite")
TEST_DB_URL = f"sqlite:///{TEST_DB_FILE}"
os.environ["SQL_CONNECTION_STRING"] = TEST_DB_URL
os.environ["APP_ENV"] = "test"

from app.db import Base, get_db
from app.models import Product, Supermarket, Price
from app.main import app


engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh schema for each test function and provide a session."""
    # Ensure file exists and schema is created
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    """Provide a TestClient that uses the test_db session for DB dependency."""
    def _override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_test_data(test_db):
    """Seed the provided `test_db` session with 3 products, 3 supermarkets and 9 prices."""
    # Products
    products = [
        Product(name="Milk", category="Dairy"),
        Product(name="Bread", category="Bakery"),
        Product(name="Eggs", category="Dairy"),
    ]
    for p in products:
        test_db.add(p)
    test_db.commit()
    for p in products:
        test_db.refresh(p)

    # Supermarkets
    supermarkets = [
        Supermarket(name="Walmart", city="New York"),
        Supermarket(name="Target", city="New York"),
        Supermarket(name="Kroger", city="New York"),
    ]
    for s in supermarkets:
        test_db.add(s)
    test_db.commit()
    for s in supermarkets:
        test_db.refresh(s)

    # Prices (3 products x 3 stores)
    prices = [
        # Milk
        Price(product_id=products[0].id, store_id=supermarkets[0].id, price=2.99),
        Price(product_id=products[0].id, store_id=supermarkets[1].id, price=2.49),
        Price(product_id=products[0].id, store_id=supermarkets[2].id, price=2.79),
        # Bread
        Price(product_id=products[1].id, store_id=supermarkets[0].id, price=1.99),
        Price(product_id=products[1].id, store_id=supermarkets[1].id, price=2.19),
        Price(product_id=products[1].id, store_id=supermarkets[2].id, price=1.89),
        # Eggs
        Price(product_id=products[2].id, store_id=supermarkets[0].id, price=3.49),
        Price(product_id=products[2].id, store_id=supermarkets[1].id, price=3.29),
        Price(product_id=products[2].id, store_id=supermarkets[2].id, price=3.69),
    ]
    for pr in prices:
        test_db.add(pr)
    test_db.commit()

    return {"products": products, "supermarkets": supermarkets, "prices": prices}
