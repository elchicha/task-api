from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

app = FastAPI(
    title="EchetoTech Product Catalog API",
    description="API for managing product catalogs",
)

# In-memory storage TODO: Improve storage implementation
products_db = {}
next_id = 1

request_timestamps = []


def reset_database():
    """Reset the in-memory database. Used for testing"""
    global next_id, products_db
    products_db.clear()
    next_id = 1


def get_database_connection():
    """
    Simulate getting a database connection.
    In real app, this would connect to PostgreSQL, MongoDB, etc.

    For testing, we can make this fail on demand.
    """
    # In production, this might be:
    # return psycopg2.connect(DATABASE_URL)

    # For our in-memory version, just return the dict
    return products_db


def rate_limit_check():
    # Check if rate limit is exceeded
    global request_timestamps
    now = datetime.now()

    request_timestamps = [
        ts for ts in request_timestamps if now - ts < timedelta(seconds=1)
    ]

    if len(request_timestamps) >= 5:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    request_timestamps.append(now)


class Product(BaseModel):
    """Model for creating a product"""

    sku: str
    name: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    description: str


class ProductResponse(BaseModel):
    """Product response model"""

    id: int
    sku: str
    name: str
    price: float
    description: str


@app.post(
    "/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
def create_product(product: Product):
    """
    Create a new product in the catalog.
    Returns 201 Created with the product data including ID.

    :param product:
    :return:
    """
    global next_id, products_db

    if product.sku in products_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product.sku}' already exists",
        )

    new_product = product.model_dump()
    new_product["id"] = next_id

    products_db[product.sku] = new_product
    next_id += 1

    return new_product


@app.get(
    "/products/{sku}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit_check)],
)
def get_product(sku: str):
    try:
        db = get_database_connection()

        if sku not in db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with SKU '{sku}' not found",
            )
        return db[sku]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error: Unable to process request"
        )


@app.put(
    "/products/{sku}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def update_product(sku: str, product: Product):
    """
    Update an existing product.
    Returns 404 if product doesn't exist.

    :param product:
    :param sku:
    :return:
    """

    if sku not in products_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found",
        )

    existing_id = products_db[sku]["id"]

    updated_product = product.model_dump()
    updated_product["id"] = existing_id

    products_db[sku] = updated_product

    return updated_product


@app.delete("/products/{sku}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(sku: str):
    if sku not in products_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found",
        )
    del products_db[sku]
