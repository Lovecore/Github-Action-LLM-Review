from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI example application!"}

def test_create_and_read_item():
    # Test creating an item
    item_data = {"name": "Test Item", "price": 10.99}
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    item_id = response.json()["item_id"]
    
    # Test reading the created item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["item"]["name"] == item_data["name"]
    assert response.json()["item"]["price"] == item_data["price"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
