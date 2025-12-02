"""
Integration tests for API endpoints
Simple smoke tests that don't require database setup
Database-dependent tests are in test_routes.py and test_api_integration.py
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
    assert response.json()["status"] == "ok"
