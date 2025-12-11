"""
Integration tests for /shopping-lists endpoints
"""

import os

# Disable the scheduler before importing app (must be before imports)
os.environ["REFRESH_SCHEDULER_ENABLED"] = "0"
os.environ["APP_ENV"] = "test"

import tempfile  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.main import app  # noqa: E402
from app.db import Base, get_db  # noqa: E402


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database per test"""
    # Create a new temporary file for each test to ensure isolation
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_url = f"sqlite:///{db_file.name}"

    # Create test engine
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    try:
        os.unlink(db_file.name)
    except Exception:
        pass


class TestShoppingListCRUD:
    """Tests for shopping list CRUD operations"""

    def test_create_shopping_list(self, client):
        response = client.post(
            "/api/v1/shopping-lists/", json={"name": "Weekly Groceries", "owner": "test_user"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Weekly Groceries"
        assert data["owner"] == "test_user"
        assert data["id"] is not None
        assert data["items"] == []

    def test_list_shopping_lists(self, client):
        # Create two lists
        client.post("/api/v1/shopping-lists/", json={"name": "List 1"})
        client.post("/api/v1/shopping-lists/", json={"name": "List 2"})

        response = client.get("/api/v1/shopping-lists/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["List 1", "List 2"]

    def test_get_shopping_list(self, client):
        # Create a list
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "My List"})
        list_id = create_response.json()["id"]

        response = client.get(f"/api/v1/shopping-lists/{list_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == list_id
        assert data["name"] == "My List"

    def test_get_nonexistent_list_returns_404(self, client):
        response = client.get("/api/v1/shopping-lists/99999")

        assert response.status_code == 404

    def test_delete_shopping_list(self, client):
        # Create a list
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "To Delete"})
        list_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/v1/shopping-lists/{list_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/v1/shopping-lists/{list_id}")
        assert get_response.status_code == 404


class TestShoppingListItems:
    """Tests for shopping list item operations"""

    def test_add_item_to_list(self, client):
        # Create a list
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "Test List"})
        list_id = create_response.json()["id"]

        # Add an item
        response = client.post(
            f"/api/v1/shopping-lists/{list_id}/items",
            json={
                "name": "Leche desnatada 1L",
                "category": "milk",
                "brand": "Hacendado",
                "variants": "desnatada,sin lactosa",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Leche desnatada 1L"
        assert data["category"] == "milk"
        assert data["brand"] == "Hacendado"
        assert data["variants"] == "desnatada,sin lactosa"
        assert data["best_store"] is None  # Not refreshed yet

    def test_add_item_to_nonexistent_list_returns_404(self, client):
        response = client.post("/api/v1/shopping-lists/99999/items", json={"name": "Test Item"})

        assert response.status_code == 404

    def test_remove_item_from_list(self, client):
        # Create list and add item
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "Test List"})
        list_id = create_response.json()["id"]

        item_response = client.post(
            f"/api/v1/shopping-lists/{list_id}/items", json={"name": "Test Item"}
        )
        item_id = item_response.json()["id"]

        # Remove item
        response = client.delete(f"/api/v1/shopping-lists/{list_id}/items/{item_id}")
        assert response.status_code == 204

        # Verify item is gone
        list_response = client.get(f"/api/v1/shopping-lists/{list_id}")
        assert len(list_response.json()["items"]) == 0

    def test_items_included_in_list_response(self, client):
        # Create list and add items
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "Test List"})
        list_id = create_response.json()["id"]

        client.post(
            f"/api/v1/shopping-lists/{list_id}/items", json={"name": "Milk", "category": "milk"}
        )
        client.post(
            f"/api/v1/shopping-lists/{list_id}/items", json={"name": "Bread", "category": "bread"}
        )

        # Get list and verify items
        response = client.get(f"/api/v1/shopping-lists/{list_id}")
        data = response.json()

        assert len(data["items"]) == 2
        item_names = [item["name"] for item in data["items"]]
        assert "Milk" in item_names
        assert "Bread" in item_names


class TestShoppingListRefresh:
    """Tests for shopping list refresh endpoint"""

    def test_refresh_returns_202_accepted(self, client):
        # Create list
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "Test List"})
        list_id = create_response.json()["id"]

        # Trigger refresh
        response = client.post(f"/api/v1/shopping-lists/{list_id}/refresh")

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["list_id"] == list_id

    def test_refresh_nonexistent_list_returns_404(self, client):
        response = client.post("/api/v1/shopping-lists/99999/refresh")

        assert response.status_code == 404


class TestResponseSchemas:
    """Tests for response schema structure"""

    def test_list_summary_includes_item_count(self, client):
        # Create list with items
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "Test List"})
        list_id = create_response.json()["id"]

        client.post(f"/api/v1/shopping-lists/{list_id}/items", json={"name": "Item 1"})
        client.post(f"/api/v1/shopping-lists/{list_id}/items", json={"name": "Item 2"})

        # Get list summaries
        response = client.get("/api/v1/shopping-lists/")
        data = response.json()

        assert len(data) == 1
        assert data[0]["item_count"] == 2

    def test_item_response_includes_comparison_fields(self, client):
        # Create list and add item
        create_response = client.post("/api/v1/shopping-lists/", json={"name": "Test List"})
        list_id = create_response.json()["id"]

        item_response = client.post(
            f"/api/v1/shopping-lists/{list_id}/items",
            json={"name": "Test Item", "category": "milk"},
        )
        data = item_response.json()

        # Verify all expected fields are present
        assert "id" in data
        assert "name" in data
        assert "brand" in data
        assert "category" in data
        assert "variants" in data
        assert "best_store" in data
        assert "best_price" in data
        assert "best_url" in data
        assert "comparison_json" in data
