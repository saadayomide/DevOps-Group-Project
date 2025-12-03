"""
Integration tests for API endpoints
These tests use the test fixtures from conftest.py to avoid SQLite threading issues
"""


def test_root_endpoint(test_client):
    """Test root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    # Health endpoint returns {"status": "ok"}
    assert response.json()["status"] == "ok"


def test_supermarkets_endpoint(test_client, seed_test_data):
    """Test supermarkets endpoint with seeded data"""
    response = test_client.get("/api/v1/supermarkets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_products_endpoint(test_client, seed_test_data):
    """Test products endpoint with seeded data"""
    response = test_client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
