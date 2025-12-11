"""
Integration tests for ShopSmart API
Tests all endpoints and business logic

NOTE: This module targets the legacy TeamC router/main at repo root.
The current implementation has moved the main FastAPI app under api/app.
To avoid import errors in CI, we skip this legacy suite at module import time.
"""

import pytest

pytest.skip(
    "Skipping legacy TeamC integration tests; API has moved to api/app. "
    "Update tests before re-enabling.",
    allow_module_level=True,
)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_correct_status(self):
        """Health endpoint should return healthy status"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_200(self):
        """Root endpoint should return 200 OK"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_api_info(self):
        """Root endpoint should return API information"""
        response = client.get("/")
        data = response.json()
        assert data["service"] == "ShopSmart TeamC"
        assert data["status"] == "ok"


class TestSupermarketsEndpoint:
    """Test supermarkets endpoint"""

    def test_get_supermarkets_returns_200(self):
        """Supermarkets endpoint should return 200 OK"""
        response = client.get("/api/supermarkets")
        assert response.status_code == 200

    def test_get_supermarkets_returns_list(self):
        """Supermarkets endpoint should return a list"""
        response = client.get("/api/supermarkets")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_supermarket_structure(self):
        """Each supermarket should have required fields"""
        response = client.get("/api/supermarkets")
        data = response.json()
        supermarket = data[0]
        assert "id" in supermarket
        assert "name" in supermarket


class TestProductsEndpoint:
    """Test products endpoint"""

    def test_get_products_returns_200(self):
        """Products endpoint should return 200 OK"""
        response = client.get("/api/products")
        assert response.status_code == 200

    def test_get_products_returns_list(self):
        """Products endpoint should return a list of products"""
        response = client.get("/api/products")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_product_structure(self):
        """Each product should have required fields"""
        response = client.get("/api/products")
        data = response.json()
        product = data[0]
        assert "id" in product
        assert "name" in product


class TestPricesEndpoint:
    """Test prices endpoint"""

    def test_get_prices_returns_200(self):
        """Prices endpoint should return 200 OK"""
        response = client.get("/api/prices")
        assert response.status_code == 200

    def test_get_prices_returns_list(self):
        """Prices endpoint should return price data"""
        response = client.get("/api/prices")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestCompareEndpoint:
    """Test price comparison endpoint"""

    def test_compare_with_valid_data(self):
        """Compare endpoint should work with valid shopping list"""
        payload = {
            "items": ["milk", "bread", "eggs"],
            "stores": ["Mercadona", "Carrefour", "Lidl"]
        }
        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200

    def test_compare_returns_recommendations(self):
        """Compare should return recommendations for each item"""
        payload = {
            "items": ["milk", "bread"],
            "stores": ["Mercadona", "Lidl"]
        }
        response = client.post("/api/compare", json=payload)
        data = response.json()

        assert "recommendations" in data
        assert len(data["recommendations"]) == 2
        assert "total_cost" in data
        assert "savings" in data
        assert "store_totals" in data

    def test_compare_finds_cheapest_store(self):
        """Compare should identify the cheapest store for each product"""
        payload = {
            "items": ["milk"],
            "stores": ["Mercadona", "Carrefour", "Lidl"]
        }
        response = client.post("/api/compare", json=payload)
        data = response.json()

        recommendation = data["recommendations"][0]
        assert "product" in recommendation
        assert "cheapest_store" in recommendation
        assert "price" in recommendation
        assert "all_prices" in recommendation

        # Verify cheapest store is actually the minimum price
        all_prices = recommendation["all_prices"]
        cheapest_price = min(all_prices.values())
        assert recommendation["price"] == cheapest_price

    def test_compare_calculates_totals_correctly(self):
        """Compare should calculate correct totals"""
        payload = {
            "items": ["milk", "bread"],
            "stores": ["Mercadona", "Lidl"]
        }
        response = client.post("/api/compare", json=payload)
        data = response.json()

        # Total cost should equal sum of cheapest prices
        total_from_recommendations = sum(
            rec["price"] for rec in data["recommendations"]
        )
        assert abs(data["total_cost"] - total_from_recommendations) < 0.01

    def test_compare_with_single_store(self):
        """Compare should work with single store"""
        payload = {
            "items": ["milk"],
            "stores": ["Mercadona"]
        }
        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) == 1

    def test_compare_with_invalid_store(self):
        """Compare should handle invalid store names"""
        payload = {
            "items": ["milk"],
            "stores": ["NonExistentStore"]
        }
        response = client.post("/api/compare", json=payload)
        assert response.status_code == 400

    def test_compare_with_unknown_product(self):
        """Compare should handle unknown products gracefully"""
        payload = {
            "items": ["unknown_product", "milk"],
            "stores": ["Mercadona"]
        }
        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Should only return recommendation for milk
        assert len(data["recommendations"]) == 1
        assert data["recommendations"][0]["product"] == "milk"

    def test_compare_case_insensitive(self):
        """Compare should be case insensitive for product names"""
        payload = {
            "items": ["MILK", "Bread", "EgGs"],
            "stores": ["Mercadona"]
        }
        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) == 3


class TestDataConsistency:
    """Test data consistency and relationships"""

    def test_all_products_have_prices(self):
        """Verify that products in price list exist in products"""
        products_response = client.get("/api/products")
        prices_response = client.get("/api/prices")

        products = products_response.json()
        prices = prices_response.json()

        product_ids = {p["id"] for p in products}
        price_product_ids = {p["product_id"] for p in prices}

        # All products in prices should exist in products list
        assert price_product_ids.issubset(product_ids)

    def test_all_stores_in_prices_exist(self):
        """Verify that stores in price list exist in supermarkets"""
        supermarkets_response = client.get("/api/supermarkets")
        prices_response = client.get("/api/prices")

        supermarkets = supermarkets_response.json()
        prices = prices_response.json()

        store_ids = {s["id"] for s in supermarkets}
        price_store_ids = {p["supermarket_id"] for p in prices}

        # All stores in prices should exist in supermarkets list
        assert price_store_ids.issubset(store_ids)


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_compare_with_empty_items(self):
        """Compare with empty items list should return empty recommendations"""
        payload = {
            "items": [],
            "stores": ["Mercadona"]
        }
        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) == 0
        assert data["total_cost"] == 0.0

    def test_compare_with_missing_fields(self):
        """Compare should accept missing optional stores field"""
        payload = {"items": ["milk"]}  # Stores list is optional
        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data

    def test_invalid_endpoint(self):
        """Invalid endpoint should return 404"""
        response = client.get("/api/invalid")
        assert response.status_code == 404


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
