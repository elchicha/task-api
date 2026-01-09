import pytest
from fastapi.testclient import TestClient
from app.api import app, reset_database


@pytest.fixture
def client():
    """Test client for our Product API"""
    reset_database()
    return TestClient(app)


class TestCreateProduct:
    """Tests for POST /products"""

    def test_create_product_returns_201(self, client):
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

    def test_create_duplicate_sku_returns_409(self, client):
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
        assert "WIDGET-001" in str(
            error_data["detail"]
        )  # Tell them which SKU conflicted

    def test_create_product_with_negative_price_returns_422(self, client):
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


class TestGetProduct:
    def test_invalid_product_retrieval_returns_404(self, client):
        """
        Test 4: Retrieving a product with an invalid SKU should return 404 Not Found

        Real support scenario: Customer's product lookup fails.
        As a support manager, your team needs to explain:
        - 404 means "the resource you requested does not exist"
        - Different from 400 (malformed request) or 409 (conflict)
        - The error should tell them which field is invalid and why
        """
        response = client.get("/products/WIDGET-003")
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    def test_valid_product_retrieval_returns_200(self, client):
        """
        Test 5: Retrieving a valid product should return 200 OK

        Real support scenario: Customer's product lookup succeeds.
        As a support manager, your team needs to explain:
        - 200 means "the request was successful"
        - The response should include the product details
        - The error should tell them which field is invalid and why
        """
        product_data = {
            "id": 1,
            "sku": "WIDGET-001",
            "name": "Widget 1",
            "price": 10.0,
            "description": "A great widget",
        }
        client.post("/products", json=product_data)

        response = client.get("/products/WIDGET-001")
        assert response.status_code == 200
        assert "id" in response.json()
        assert "sku" in response.json()
        assert "name" in response.json()
        assert "price" in response.json()
        assert "description" in response.json()


class TestUpdateProduct:
    def test_update_products_return_200(self, client):
        """
        Test: PUT /products/{sku} updates an existing product and returns 200 OK
        :param client:
        :return:
        """
        create_data = {
            "sku": "WIDGET-001",
        }

    def test_update_product_returns_200(self, client):
        """
        Test: PUT /products/{sku} updates existing product and returns 200 OK
        :param client:
        :return:
        """
        create_data = {
            "sku": "WIDGET-001",
            "name": "Blue Widget",
            "price": 29.99,
            "description": "Original description",
        }
        client.post("/products", json=create_data)

        update_data = {
            "sku": "WIDGET-001",
            "name": "Updated Blue Widget",
            "price": 29.99,
            "description": "Updated description",
        }

        response = client.put("/products/WIDGET-001", json=update_data)
        assert response.status_code == 200
        assert response.json()["sku"] == "WIDGET-001"
        assert response.json()["name"] == "Updated Blue Widget"
        assert response.json()["price"] == 29.99
        assert response.json()["description"] == "Updated description"

    def test_update_nonexistent_product_returns_404(self, client):
        """
        Test: PUT on non-existent product returns 404

        We're doing update-only PUT (not upsert).
        If you want to create, use POST.
        """
        update_data = {
            "sku": "DOES-NOT-EXIST",
            "name": "Ghost Product",
            "price": 99.99,
            "description": "This product was never created",
        }

        response = client.put("/products/DOES-NOT-EXIST", json=update_data)

        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
