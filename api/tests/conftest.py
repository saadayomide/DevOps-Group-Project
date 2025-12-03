"""
Pytest configuration and fixtures for testing
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Set test environment BEFORE importing any app modules
os.environ["SQL_CONNECTION_STRING"] = "sqlite:///:memory:"
os.environ["APP_ENV"] = "test"

# Now import app modules
from app.db import Base, get_db  # noqa: E402
from app.models import Product, Supermarket, Price  # noqa: E402
from app.config import settings  # noqa: E402
from app.routes import health, products, supermarkets, prices, compare  # noqa: E402
from app.middleware import LoggingMiddleware  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware  # noqa: E402

# Compatibility constants for root-level tests (tests/test_prices.py)
PRODUCT_COUNT = 10
SUPERMARKET_COUNT = 3
PRICE_COUNT = 27


# Test database URL (SQLite in-memory for fast tests)
TEST_DATABASE_URL = "sqlite:///:memory:"


def create_test_app():
    """Create a test FastAPI app"""
    test_app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # Add middleware
    test_app.add_middleware(LoggingMiddleware)
    test_app.add_middleware(
        FastAPICORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    test_app.include_router(health.router, tags=["Health"])
    test_app.include_router(
        supermarkets.router, prefix=f"{settings.api_prefix}/supermarkets", tags=["Supermarkets"]
    )
    test_app.include_router(
        products.router, prefix=f"{settings.api_prefix}/products", tags=["Products"]
    )
    test_app.include_router(prices.router, prefix=f"{settings.api_prefix}/prices", tags=["Prices"])
    test_app.include_router(
        compare.router, prefix=f"{settings.api_prefix}/compare", tags=["Compare"]
    )

    @test_app.get("/")
    async def root():
        return {
            "message": "Welcome to Product Comparison API",
            "version": settings.app_version,
            "docs": "/docs",
        }

    return test_app


# Create test app
app = create_test_app()


@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database for each test function
    Uses SQLite in-memory database for fast, isolated tests
    """
    # Create test engine (SQLite doesn't support max_overflow, pool_size)
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Create all tables using Base from app.db
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    """
    Create a test client with test database dependency override
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_test_data(test_db):
    """
    Seed test database with 3 products × 3 stores
    Returns dict with created objects for easy access in tests
    """
    # Create 3 products
    products = [
        Product(name="Milk", category="Dairy"),
        Product(name="Bread", category="Bakery"),
        Product(name="Eggs", category="Dairy"),
    ]
    for product in products:
        test_db.add(product)
    test_db.commit()

    # Refresh to get IDs
    for product in products:
        test_db.refresh(product)

    # Create 3 supermarkets
    supermarkets = [
        Supermarket(name="Walmart", city="New York"),
        Supermarket(name="Target", city="New York"),
        Supermarket(name="Kroger", city="New York"),
    ]
    for supermarket in supermarkets:
        test_db.add(supermarket)
    test_db.commit()

    # Refresh to get IDs
    for supermarket in supermarkets:
        test_db.refresh(supermarket)

    # Create prices: 3 products × 3 stores = 9 prices
    # Product 1 (Milk): $2.99, $2.49, $2.79
    # Product 2 (Bread): $1.99, $2.19, $1.89
    # Product 3 (Eggs): $3.49, $3.29, $3.69
    prices = [
        # Milk prices
        Price(product_id=products[0].id, store_id=supermarkets[0].id, price=2.99),
        Price(product_id=products[0].id, store_id=supermarkets[1].id, price=2.49),  # Cheapest
        Price(product_id=products[0].id, store_id=supermarkets[2].id, price=2.79),
        # Bread prices
        Price(product_id=products[1].id, store_id=supermarkets[0].id, price=1.99),
        Price(product_id=products[1].id, store_id=supermarkets[1].id, price=2.19),
        Price(product_id=products[1].id, store_id=supermarkets[2].id, price=1.89),  # Cheapest
        # Eggs prices
        Price(product_id=products[2].id, store_id=supermarkets[0].id, price=3.49),
        Price(product_id=products[2].id, store_id=supermarkets[1].id, price=3.29),  # Cheapest
        Price(product_id=products[2].id, store_id=supermarkets[2].id, price=3.69),
    ]
    for price in prices:
        test_db.add(price)
    test_db.commit()

    return {"products": products, "supermarkets": supermarkets, "prices": prices}
