"""
Integration test for the shopping list refresh flow.
This test uses an in-memory SQLite database and monkeypatches the scraper to avoid network.
"""
import asyncio
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import ShoppingList, ShoppingListItem, Supermarket, Product, Price
from app.services.refresh_service import refresh_shopping_list


class DummyOffer:
    def __init__(self, name, price, category, store="Mercadona", url=None):
        self.name = name
        self.price = price
        self.category_name = category
        self.subcategory_name = ""
        self.store = store
        self.url = url


async def fake_scrape(self, query):
    # Return deterministic offers for test
    return [
        {"name": "Leche desnatada 1L", "price": 1.2, "category": "milk", "subcategory": "desnatada", "store": "Mercadona", "url": "http://m/1"},
        {"name": "Leche entera 1L", "price": 1.0, "category": "milk", "subcategory": "entera", "store": "Mercadona", "url": "http://m/2"},
    ]


def test_refresh_updates_items(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create shopping list and item
    sl = ShoppingList(name="Test List")
    session.add(sl)
    session.commit()

    item = ShoppingListItem(shopping_list_id=sl.id, name="Leche 1L", brand=None, category="milk", variants="desnatada")
    session.add(item)
    session.commit()

    # Monkeypatch scraper
    import app.services.scraper_service as ss

    monkeypatch.setattr(ss.ScraperService, "scrape_mercadona_product", fake_scrape)

    summary = refresh_shopping_list(sl.id, session)

    session.refresh(item)
    assert summary["updated_items"] == 1
    assert item.best_price is not None
    assert item.comparison_json is not None
    # selected should be present in comparison_json
    assert item.comparison_json.get("selected") is not None
