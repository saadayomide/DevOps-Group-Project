from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"

def test_compare_endpoint_smoke():
    payload = {"items": ["milk","bread"]}
    r = client.post("/teamc/compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "recommendations" in body
    assert "total_cost" in body
