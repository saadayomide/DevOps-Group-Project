"""
Integration tests for catalog routes.
"""
from fastapi import status


def test_list_categories_returns_milk_and_eggs(test_client):
    response = test_client.get("/api/v1/catalog/categories")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

    codes = {item["code"] for item in data}
    assert "milk" in codes
    assert "eggs" in codes


def test_get_category_detail_milk(test_client):
    response = test_client.get("/api/v1/catalog/categories/milk")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["code"] == "milk"
    assert data["label"] == "Leche"
    assert "L" in data["units"]
    assert "desnatada" in data["variants"]


def test_get_category_detail_unknown_returns_404(test_client):
    response = test_client.get("/api/v1/catalog/categories/unknown")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    payload = response.json()
    if "detail" in payload:
        assert payload["detail"] == "Unknown category"
    else:
        assert payload.get("message") == "Unknown category"
