"""
Integration tests for API endpoints
Can be used in CI/CD pipelines and smoke tests
"""

from fastapi import status


class TestAPIIntegration:
    """Integration tests for API endpoints"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"

    def test_get_products_returns_more_than_zero_rows(self, test_client, seed_test_data):
        """
        Integration Test: GET /products returns >0 rows

        This test verifies that the products endpoint returns data,
        which is required for the integration test suite.
        """
        response = test_client.get("/api/v1/products/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Products endpoint must return more than 0 rows"

        # Verify structure
        for product in data:
            assert "id" in product
            assert "name" in product
            assert isinstance(product["id"], int)
            assert isinstance(product["name"], str)

    def test_post_compare_with_3_items_returns_correct_mapping_and_totals(
        self, test_client, seed_test_data
    ):
        """
        Integration Test: POST /compare with 3 items returns correct mapping & totals

        This test verifies:
        1. Response has correct structure
        2. Items are correctly mapped to stores
        3. Store totals are calculated correctly
        4. Overall total is present
        """
        request_body = {
            "items": ["Milk", "Bread", "Eggs"],
            "stores": ["Walmart", "Target", "Kroger"],
        }

        response = test_client.post("/api/v1/compare", json=request_body)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "items" in data
        assert "storeTotals" in data
        assert "overallTotal" in data
        assert "unmatched" in data

        assert isinstance(data["items"], list)
        assert isinstance(data["storeTotals"], list)
        assert isinstance(data["overallTotal"], (int, float))
        assert isinstance(data["unmatched"], list)

        # Verify items structure
        for item in data["items"]:
            assert "name" in item
            assert "store" in item
            assert "price" in item
            assert isinstance(item["name"], str)
            assert isinstance(item["store"], str)
            assert isinstance(item["price"], (int, float))
            assert item["price"] > 0

        # Verify storeTotals structure
        for store_total in data["storeTotals"]:
            assert "store" in store_total
            assert "total" in store_total
            assert isinstance(store_total["store"], str)
            assert isinstance(store_total["total"], (int, float))
            assert store_total["total"] >= 0

        # Verify mapping: each item should have a store and price
        item_names = [item["name"] for item in data["items"]]
        assert len(item_names) > 0, "Should have at least some matched items"

        # Verify store totals match requested stores
        store_names = [st["store"] for st in data["storeTotals"]]
        for store_name in store_names:
            # Store should be in requested stores (case-insensitive)
            found = any(
                req_store.lower() == store_name.lower() for req_store in request_body["stores"]
            )
            assert found, f"Store {store_name} should be in requested stores"

        # Verify totals are calculated correctly
        # Calculate expected totals per store from items
        calculated_totals = {}
        for item in data["items"]:
            store = item["store"]
            if store not in calculated_totals:
                calculated_totals[store] = 0.0
            calculated_totals[store] += item["price"]

        # Verify store totals match calculated values (with tolerance for floating point)
        for store_total in data["storeTotals"]:
            store = store_total["store"]
            expected_total = calculated_totals.get(store, 0.0)
            assert (
                abs(store_total["total"] - expected_total) < 0.01
            ), f"Store total for {store} should be {expected_total}, got {store_total['total']}"

        # Verify overallTotal is reasonable
        if data["storeTotals"]:
            assert data["overallTotal"] >= 0
            # overallTotal should not exceed the sum of store totals
            total_sum = sum(st["total"] for st in data["storeTotals"])
            assert data["overallTotal"] <= total_sum

    def test_post_compare_with_3_items_handles_unmatched(self, test_client, seed_test_data):
        """
        Integration Test: POST /compare handles unmatched items correctly
        """
        request_body = {
            "items": ["Milk", "Bread", "NonexistentProduct"],
            "stores": ["Walmart", "Target", "Kroger"],
        }

        response = test_client.post("/api/v1/compare", json=request_body)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have unmatched items
        assert "NonexistentProduct" in data["unmatched"]

        # Should still have matched items
        matched_names = [item["name"] for item in data["items"]]
        assert "Milk" in matched_names or "Bread" in matched_names

    def test_get_supermarkets_returns_data(self, test_client, seed_test_data):
        """Test GET /supermarkets returns data"""
        response = test_client.get("/api/v1/supermarkets/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify structure
        for supermarket in data:
            assert "id" in supermarket
            assert "name" in supermarket

    def test_get_prices_returns_data(self, test_client, seed_test_data):
        """Test GET /prices returns data"""
        response = test_client.get("/api/v1/prices/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify structure
        for price in data:
            assert "id" in price
            assert "product_id" in price
            assert "store_id" in price
            assert "price" in price
