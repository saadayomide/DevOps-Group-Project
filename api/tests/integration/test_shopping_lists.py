"""
Integration tests for shopping list orchestrator (no scrapers yet).
"""
from datetime import datetime

from fastapi import status


def test_create_shopping_list(test_client):
    payload = {
        "name": "Compra fin de semana",
        "items": [
            {"category": "milk", "brand": "Hacendado", "variants": ["desnatada"], "quantity": 2, "unit": "unit"},
            {"category": "eggs", "brand": None, "variants": ["L"], "quantity": 12, "unit": "unit"},
        ],
    }

    response = test_client.post("/api/v1/shopping-lists/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["id"] > 0
    assert data["name"] == payload["name"]
    assert len(data["items"]) == 2

    first = data["items"][0]
    assert first["category"] == "milk"
    assert first["brand"] == "Hacendado"
    assert first["best_store"] is None
    assert first["best_price"] is None


def test_get_shopping_list(test_client):
    create_payload = {
        "name": "Compra express",
        "items": [
            {"category": "bread", "brand": "Bimbo", "variants": ["blanco"], "quantity": 1, "unit": "unit"},
        ],
    }
    create_resp = test_client.post("/api/v1/shopping-lists/", json=create_payload)
    list_id = create_resp.json()["id"]

    get_resp = test_client.get(f"/api/v1/shopping-lists/{list_id}")
    assert get_resp.status_code == status.HTTP_200_OK

    data = get_resp.json()
    assert data["id"] == list_id
    assert data["name"] == create_payload["name"]
    assert len(data["items"]) == 1
    assert data["items"][0]["category"] == "bread"


def test_refresh_shopping_list(test_client):
    payload = {
        "name": "Lista con refresh",
        "items": [{"category": "milk", "brand": None, "variants": [], "quantity": 1, "unit": "unit"}],
    }
    create_resp = test_client.post("/api/v1/shopping-lists/", json=payload)
    body = create_resp.json()
    list_id = body["id"]
    original_last_refreshed = datetime.fromisoformat(body["last_refreshed"])

    refresh_resp = test_client.post(f"/api/v1/shopping-lists/{list_id}/refresh")
    assert refresh_resp.status_code == status.HTTP_200_OK

    refreshed = refresh_resp.json()
    refreshed_last = datetime.fromisoformat(refreshed["last_refreshed"])
    assert refreshed_last >= original_last_refreshed
