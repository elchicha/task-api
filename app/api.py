from typing import Optional

from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(
    title="EchetoTech Product Catalog API",
    description="API for managing product catalogs",
)

# In-memory storage TODO: Improve storage implementation
products_db = {}
next_id = 1


class Product(BaseModel):
    """Model for creating a product"""

    sku: str
    name: str
    price: float
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
    global next_id

    new_product = product.model_dump()
    new_product["id"] = next_id
    next_id += 1

    return new_product
