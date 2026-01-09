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
        "description": "A beautiful blue widget",
    }

    response = client.post("/products", json=product_data)

    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "WIDGET-001"
    assert data["name"] == "Blue Widget"
    assert data["price"] == 29.99
    assert "id" in data


def test_create_duplicate_sku_returns_409(client):
    """
    Test 2: Creating a product with duplicate SKU should return 409 Conflict

    This is a CLIENT ERROR (4xx) - they're trying to create something that already exists.

    Real support scenario: Customer's bulk import tries to create the same product twice.
    As a support manager, you need to help your team explain:
    - This is a 409 (Conflict), not 500 (our bug)
    - The error message should tell them which SKU conflicted
    - They need to update instead of create
    """
    # First, create a product successfully
    product_data = {
        "sku": "WIDGET-001",
        "name": "Blue Widget",
        "price": 29.99,
        "description": "A beautiful blue widget",
    }

    response1 = client.post("/products", json=product_data)
    assert response1.status_code == 201  # First one succeeds

    # Now try to create the SAME SKU again
    duplicate_data = {
        "sku": "WIDGET-001",  # Same SKU!
        "name": "Red Widget",  # Different name, doesn't matter
        "price": 19.99,
        "description": "A different widget",
    }

    response2 = client.post("/products", json=duplicate_data)

    # Should get 409 Conflict
    assert response2.status_code == 409

    # Error response should be helpful for troubleshooting
    error_data = response2.json()
    assert "detail" in error_data  # FastAPI's standard error format
    assert "WIDGET-001" in str(error_data["detail"])  # Tell them which SKU conflicted


def test_create_product_with_negative_price_returns_422(client):
    """
    Test 3: Creating a product with a negative price should return 422 Unprocessable Entity

    This is validation - the data format is correct (float), but the VALUE is invalid.

    Real support scenario: Customer's CSV import has a data error.
    As a support manager, your team needs to explain:
    - 422 means "we understood your request, but the data is invalid"
    - Different from 400 (malformed request) or 409 (conflict)
    - The error should tell them which field is invalid and why
    """
    product_data = {
        "sku": "WIDGET-002",
        "name": "Cheap Widget",
        "price": -10.00,
        "description": "This shouldn't work",
    }

    response = client.post("/products", json=product_data)

    # Should get 422 Unprocessable Entity
    assert response.status_code == 422

    # Error should mention price
    error_data = response.json()
    assert "detail" in error_data
    # FastAPI validation errors have a specific structure
    assert any("price" in str(error).lower() for error in error_data["detail"])
