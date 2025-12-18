"""
Integration test for the refresh endpoint.
Starts a TestClient, seeds an in-memory DB, monkeypatches scraper to return deterministic offers,
then POSTs to the refresh endpoint and polls the DB for updates.
"""

import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import ShoppingList, ShoppingListItem
from app.main import app


# Fake offers (synchronous) returned by ScraperManager.get_offers
def fake_get_offers(self, query):
    return [
        {
            "name": "Leche desnatada 1L",
            "price": 1.2,
            "category": "milk",
            "subcategory": "desnatada",
            "store": "Mercadona",
            "url": "http://m/1",
        },
        {
            "name": "Leche entera 1L",
            "price": 1.0,
            "category": "milk",
            "subcategory": "entera",
            "store": "Mercadona",
            "url": "http://m/2",
        },
    ]


def test_refresh_endpoint_background(monkeypatch, tmp_path):
    # Use a temporary SQLite file so the background task (separate connection) can see changes
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    # Monkeypatch SessionLocal to use our test DB for the duration of the test
    monkeypatch.setattr("app.db.SessionLocal", TestSession)

    # Seed data
    db = TestSession()
    sl = ShoppingList(name="TestList")
    db.add(sl)
    db.commit()
    db.refresh(sl)
    # capture the id before closing the session to avoid DetachedInstance access
    sl_id = sl.id
    item = ShoppingListItem(
        shopping_list_id=sl_id, name="Leche 1L", brand=None, category="milk", variants="desnatada"
    )
    db.add(item)
    db.commit()
    db.close()

    # Patch ScraperManager.get_offers to avoid network
    import app.services.scrapers.manager as sm

    monkeypatch.setattr(sm.ScraperManager, "get_offers", fake_get_offers)

    client = TestClient(app)
    resp = client.post(f"/api/v1/refresh/{sl_id}")
    assert resp.status_code == 202

    # Poll for the background job to complete (timeout after a few seconds)
    start = time.time()
    updated = False
    while time.time() - start < 5:
        db = TestSession()
        refreshed = db.get(ShoppingList, sl_id)
        if refreshed and refreshed.last_refreshed:
            updated = True
            db.close()
            break
        db.close()
        time.sleep(0.2)

    assert updated, "Background refresh did not complete in time"
