from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_product_validation() -> None:
    assert client.get("/products/0").status_code == 400

def test_product_lookup() -> None:
    response = client.get("/products/42")
    assert response.status_code == 200
    assert response.json()["id"] == 42
