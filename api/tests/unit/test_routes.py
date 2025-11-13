"""
Unit tests for other routes (products, supermarkets, prices)
"""
import pytest
from fastapi import status


class TestProductsRoute:
    """Test cases for products routes"""
    
    def test_get_products_empty(self, test_client, test_db):
        """Test GET /products with empty database"""
        # Tables are created by test_db fixture
        response = test_client.get("/api/v1/products/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_get_products_with_data(self, test_client, seed_test_data):
        """Test GET /products with seeded data"""
        response = test_client.get("/api/v1/products/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # 3 products seeded
        
        # Verify structure (id and name only)
        for product in data:
            assert "id" in product
            assert "name" in product
            assert "category" not in product  # Should not include category
    
    def test_get_products_with_search(self, test_client, seed_test_data):
        """Test GET /products with search query"""
        response = test_client.get("/api/v1/products/?q=Milk")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any("Milk" in p["name"] for p in data)
    
    def test_get_products_with_limit(self, test_client, seed_test_data):
        """Test GET /products with limit"""
        response = test_client.get("/api/v1/products/?limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2
    
    def test_get_product_by_id(self, test_client, seed_test_data):
        """Test GET /products/{id}"""
        # First get all products to find an ID
        products_response = test_client.get("/api/v1/products/")
        products = products_response.json()
        product_id = products[0]["id"]
        
        response = test_client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == product_id
        assert "name" in data
        assert "category" in data  # Full schema includes category
    
    def test_get_product_not_found(self, test_client, test_db):
        """Test GET /products/{id} with non-existent ID"""
        # Tables are created by test_db fixture
        response = test_client.get("/api/v1/products/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"] == "NotFound"


class TestSupermarketsRoute:
    """Test cases for supermarkets routes"""
    
    def test_get_supermarkets_empty(self, test_client, test_db):
        """Test GET /supermarkets with empty database"""
        # Tables are created by test_db fixture
        response = test_client.get("/api/v1/supermarkets/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_get_supermarkets_with_data(self, test_client, seed_test_data):
        """Test GET /supermarkets with seeded data"""
        response = test_client.get("/api/v1/supermarkets/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # 3 supermarkets seeded
        
        # Verify structure (id and name only)
        for supermarket in data:
            assert "id" in supermarket
            assert "name" in supermarket
            assert "city" not in supermarket  # Should not include city
    
    def test_get_supermarket_by_id(self, test_client, seed_test_data):
        """Test GET /supermarkets/{id}"""
        # First get all supermarkets to find an ID
        supermarkets_response = test_client.get("/api/v1/supermarkets/")
        supermarkets = supermarkets_response.json()
        supermarket_id = supermarkets[0]["id"]
        
        response = test_client.get(f"/api/v1/supermarkets/{supermarket_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == supermarket_id
        assert "name" in data
        assert "city" in data  # Full schema includes city
    
    def test_get_supermarket_not_found(self, test_client, test_db):
        """Test GET /supermarkets/{id} with non-existent ID"""
        # Tables are created by test_db fixture
        response = test_client.get("/api/v1/supermarkets/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"] == "NotFound"


class TestPricesRoute:
    """Test cases for prices routes"""
    
    def test_get_prices_empty(self, test_client, test_db):
        """Test GET /prices with empty database"""
        # Tables are created by test_db fixture
        response = test_client.get("/api/v1/prices/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_get_prices_with_data(self, test_client, seed_test_data):
        """Test GET /prices with seeded data"""
        response = test_client.get("/api/v1/prices/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 9  # 3 products × 3 stores = 9 prices
        
        # Verify structure
        for price in data:
            assert "id" in price
            assert "product_id" in price
            assert "store_id" in price
            assert "price" in price
    
    def test_get_prices_filter_by_product(self, test_client, seed_test_data):
        """Test GET /prices?productId=X"""
        # Get a product ID
        products_response = test_client.get("/api/v1/products/")
        products = products_response.json()
        product_id = products[0]["id"]
        
        response = test_client.get(f"/api/v1/prices/?productId={product_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # Should have 3 prices (one per store)
        assert all(p["product_id"] == product_id for p in data)
    
    def test_get_prices_filter_by_store(self, test_client, seed_test_data):
        """Test GET /prices?storeId=X"""
        # Get a store ID
        stores_response = test_client.get("/api/v1/supermarkets/")
        stores = stores_response.json()
        store_id = stores[0]["id"]
        
        response = test_client.get(f"/api/v1/prices/?storeId={store_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # Should have 3 prices (one per product)
        assert all(p["store_id"] == store_id for p in data)
    
    def test_get_prices_filter_by_both(self, test_client, seed_test_data):
        """Test GET /prices?productId=X&storeId=Y"""
        # Get IDs
        products_response = test_client.get("/api/v1/products/")
        products = products_response.json()
        product_id = products[0]["id"]
        
        stores_response = test_client.get("/api/v1/supermarkets/")
        stores = stores_response.json()
        store_id = stores[0]["id"]
        
        response = test_client.get(f"/api/v1/prices/?productId={product_id}&storeId={store_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1  # Should have 1 price
        assert data[0]["product_id"] == product_id
        assert data[0]["store_id"] == store_id
    
    def test_get_price_by_id(self, test_client, seed_test_data):
        """Test GET /prices/{id}"""
        # Get a price ID
        prices_response = test_client.get("/api/v1/prices/")
        prices = prices_response.json()
        price_id = prices[0]["id"]
        
        response = test_client.get(f"/api/v1/prices/{price_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == price_id
    
    def test_get_price_not_found(self, test_client, test_db):
        """Test GET /prices/{id} with non-existent ID"""
        # Tables are created by test_db fixture
        response = test_client.get("/api/v1/prices/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"] == "NotFound"
    
    def test_get_prices_invalid_query_params(self, test_client, seed_test_data):
        """Test GET /prices with invalid query parameters"""
        # Invalid productId type
        response = test_client.get("/api/v1/prices/?productId=abc")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid storeId type
        response = test_client.get("/api/v1/prices/?storeId=xyz")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

