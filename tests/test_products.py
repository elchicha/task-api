import pytest
from fastapi.testclient import TestClient
from app.api import app

@pytest.fixture
def client():
    """Test client for our Product API"""
    return TestClient(app)


def test_create_product_returns_201(client):
    """
    Test 1: POST /products should create a product and return 201 Created
    """
    product_data = {
        "sku": "WIDGET-001",
        "name": "Blue Widget",
        "price": 29.99,
        "description": "A beautiful blue widget"
    }

    response = client.post('/products', json=product_data)

    assert response.status_code == 201
    data = response.json()
    assert data['sku'] == "WIDGET-001"
    assert data['name'] == "Blue Widget"
    assert data['price'] == 29.99
    assert 'id' in data