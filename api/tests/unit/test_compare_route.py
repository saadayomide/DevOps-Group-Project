"""
Unit tests for compare route endpoint
Tests HTTP endpoints with TestClient
"""
import pytest
from fastapi import status


class TestCompareRoute:
    """Test cases for POST /api/v1/compare endpoint"""
    
    def test_compare_success_all_items_matched(self, test_client, seed_test_data):
        """
        Test successful comparison with all items matched
        """
        response = test_client.post(
            "/api/v1/compare",
            json={
                "items": ["Milk", "Bread", "Eggs"],
                "stores": ["Walmart", "Target", "Kroger"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "storeTotals" in data
        assert "overallTotal" in data
        assert "unmatched" in data
        
        assert len(data["items"]) == 3
        assert len(data["unmatched"]) == 0
        
        # Verify structure
        for item in data["items"]:
            assert "name" in item
            assert "store" in item
            assert "price" in item
            assert isinstance(item["price"], (int, float))
            assert item["price"] > 0
    
    def test_empty_items_returns_400(self, test_client, seed_test_data):
        """
        Test Case: Empty items → 400 BadRequest
        """
        response = test_client.post(
            "/api/v1/compare",
            json={
                "items": [],
                "stores": ["Walmart", "Target"]
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["error"] == "BadRequest"
        assert "items cannot be empty" in data["message"].lower()
    
    def test_empty_stores_returns_400(self, test_client, seed_test_data):
        """
        Test Case: Empty stores → 400 BadRequest
        """
        response = test_client.post(
            "/api/v1/compare",
            json={
                "items": ["Milk", "Bread"],
                "stores": []
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["error"] == "BadRequest"
        assert "stores cannot be empty" in data["message"].lower()
    
    def test_invalid_request_body_returns_422(self, test_client, seed_test_data):
        """
        Test Case: Invalid request body → 422 UnprocessableEntity
        """
        # Missing items field
        response = test_client.post(
            "/api/v1/compare",
            json={
                "stores": ["Walmart"]
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error"] == "UnprocessableEntity"
    
    def test_invalid_items_type_returns_422(self, test_client, seed_test_data):
        """
        Test Case: Invalid items type → 422 UnprocessableEntity
        """
        response = test_client.post(
            "/api/v1/compare",
            json={
                "items": "not an array",
                "stores": ["Walmart"]
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error"] == "UnprocessableEntity"
    
    def test_unknown_stores_handled_gracefully(self, test_client, seed_test_data):
        """
        Test Case: Unknown stores are ignored silently
        
        Note: Based on implementation, unknown stores are ignored
        """
        response = test_client.post(
            "/api/v1/compare",
            json={
                "items": ["Milk", "Bread"],
                "stores": ["Walmart", "UnknownStore", "Target"]
            }
        )
        
        # Should return 200 (unknown stores ignored)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should still return results for known stores
        assert len(data["items"]) >= 0  # May be 0 if no matches, but should not error
        
        # Store totals should only include known stores
        store_names = [total["store"] for total in data["storeTotals"]]
        assert "UnknownStore" not in store_names
    
    def test_unmatched_products_in_response(self, test_client, seed_test_data):
        """
        Test Case: Unmatched products appear in unmatched list
        """
        response = test_client.post(
            "/api/v1/compare",
            json={
                "items": ["Milk", "NonexistentProduct", "Bread"],
                "stores": ["Walmart", "Target", "Kroger"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have unmatched items
        assert "NonexistentProduct" in data["unmatched"]
        
        # Should still have matched items
        matched_names = [item["name"] for item in data["items"]]
        assert "Milk" in matched_names or "Bread" in matched_names
    
    def test_response_structure(self, test_client, seed_test_data):
        """
        Test Case: Response has correct structure
        """
        response = test_client.post(
            "/api/v1/compare",
            json={
                "items": ["Milk"],
                "stores": ["Walmart"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify required fields
        assert "items" in data
        assert isinstance(data["items"], list)
        assert "storeTotals" in data
        assert isinstance(data["storeTotals"], list)
        assert "overallTotal" in data
        assert isinstance(data["overallTotal"], (int, float))
        assert "unmatched" in data
        assert isinstance(data["unmatched"], list)
        
        # Verify item structure
        if data["items"]:
            item = data["items"][0]
            assert "name" in item
            assert "store" in item
            assert "price" in item
        
        # Verify store total structure
        if data["storeTotals"]:
            store_total = data["storeTotals"][0]
            assert "store" in store_total
            assert "total" in store_total

