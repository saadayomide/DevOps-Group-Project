"""
Integration tests for API endpoints
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_supermarkets_endpoint():
    """Test supermarkets endpoint"""
    response = client.get("/api/v1/supermarkets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_products_endpoint():
    """Test products endpoint"""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
