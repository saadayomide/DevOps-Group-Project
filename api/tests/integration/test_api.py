"""
Integration tests for API endpoints
Simple smoke tests that don't require database setup
Database-dependent tests are in test_routes.py and test_api_integration.py
"""
import pytest


def test_root_endpoint(test_client):
def test_root_endpoint(test_client):
    """Test root endpoint"""
    response = test_client.get("/")
    response = test_client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(test_client):
def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/health")
    response = test_client.get("/health")
    assert response.status_code == 200
    # App returns canonical {"status": "ok"} in tests
    assert response.json()["status"] == "ok"


def test_supermarkets_endpoint(test_client):
    """Test supermarkets endpoint"""
    response = test_client.get("/api/v1/supermarkets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_products_endpoint(test_client):
    """Test products endpoint"""
    response = test_client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

