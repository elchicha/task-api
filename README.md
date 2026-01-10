# Task API - Learning HTTP Status Codes Through Building

A Product Catalog API built with FastAPI and Test-Driven Development to deeply understand HTTP status codes and API error handling.

## Why This Exists

As a Support Engineering Manager, I realized I was telling my team to "check if it's 4xx or 5xx" without truly understanding the nuances. Reading documentation wasn't enough—I needed to build it myself.

This project implements every major HTTP status code scenario through TDD, forcing me to answer questions like:
- Why is duplicate data 409 and not 400?
- When is something 422 versus 400?
- What's the difference between 500 and 503?

**Read the full story:** [Building Better Error Responses for SaaS](https://echetotech.com) (blog post coming soon)

## What's Implemented

### Endpoints
- `POST /products` - Create a product
- `GET /products/{sku}` - Get a product by SKU
- `PUT /products/{sku}` - Update a product
- `DELETE /products/{sku}` - Delete a product

### Status Codes Covered

**Success (2xx):**
- 200 OK - Successful read/update
- 201 Created - Successful creation
- 204 No Content - Successful deletion

**Client Errors (4xx):**
- 404 Not Found - Product doesn't exist
- 409 Conflict - Duplicate SKU
- 422 Unprocessable Entity - Invalid data (negative price)
- 429 Too Many Requests - Rate limiting

**Server Errors (5xx):**
- 500 Internal Server Error - Database connection failure
- 503 Service Unavailable - Maintenance mode

### Features
- ✅ Test-Driven Development (14 passing tests)
- ✅ Rate limiting (5 requests/second, sliding window)
- ✅ Pydantic validation with helpful error messages
- ✅ Proper error handling (try/except patterns)
- ✅ Maintenance mode simulation
- ✅ Database connection mocking for testing

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation
```bash
# Clone the repo
git clone https://github.com/elchicha/task-api.git
cd task-api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the API
```bash
python app/api.py
```

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Run the Tests
```bash
# Run all tests
pytest tests/test_products.py -v

# Run specific test class
pytest tests/test_products.py::TestCreateProduct -v

# Run with coverage
pytest tests/test_products.py --cov=app --cov-report=html
```

## Project Structure
```
task-api/
├── app/
│   ├── __init__.py
│   └── api.py              # FastAPI application & endpoints
├── tests/
│   ├── __init__.py
│   └── test_products.py    # All test scenarios
├── requirements.txt         # Python dependencies
└── README.md
```

## Learning Through the Tests

Each test demonstrates a specific HTTP status code scenario. The test names tell you what they're testing:
```python
# Client Errors (4xx)
test_create_product_returns_201()              # Happy path
test_create_duplicate_sku_returns_409()        # Conflict scenario
test_create_product_with_negative_price_returns_422()  # Validation
test_get_nonexistent_product_returns_404()     # Not found
test_too_many_requests_returns_429()           # Rate limiting

# Server Errors (5xx)
test_database_connection_failure_returns_500() # Unexpected error
test_service_maintenance_returns_503()         # Known downtime
```

Read the test, run it, then look at the implementation. That's how I learned.

## Key Patterns Demonstrated

### 1. The 4xx vs 5xx Rule
```python
# 4xx = Client did something wrong
if product.sku in products_db:
    raise HTTPException(409, "Product already exists")  # Their duplicate

# 5xx = Server did something wrong
except Exception as e:
    raise HTTPException(500, "Internal server error")  # Our bug
```

### 2. Specific Error Messages
```python
# Bad
raise HTTPException(404, "Not found")

# Good
raise HTTPException(404, f"Product with SKU '{sku}' not found")
```

### 3. Pydantic Validation
```python
class Product(BaseModel):
    sku: str
    name: str
    price: float = Field(gt=0)  # Automatically returns 422 if violated
    description: str
```

### 4. Rate Limiting with Sliding Window
```python
def rate_limit_check():
    # Remove old timestamps
    request_timestamps = [ts for ts in request_timestamps 
                         if now - ts < timedelta(seconds=1)]
    
    # Check limit
    if len(request_timestamps) >= 5:
        raise HTTPException(429, "Rate limit exceeded")
```

### 5. Error Handling in Endpoints
```python
try:
    db = get_database_connection()  # Might fail
    # ... do work
except HTTPException:
    raise  # Re-raise intentional errors (404, 409, etc.)
except Exception:
    raise HTTPException(500, "Internal server error")  # Catch bugs
```

## What I Learned

**Before this project:**
- Vague understanding of status codes
- "4xx = client, 5xx = server" (but fuzzy on specifics)
- Pattern-matching rather than true understanding

**After this project:**
- Deep understanding of when to use each code
- Confidence explaining to my team
- Appreciation for FastAPI's automatic validation
- Better error message design skills

**Key insight:** The 4xx/5xx split is about **fault** (who needs to fix it), not **severity** (how bad it is).

## Technologies Used

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type hints
- **Pytest** - Testing framework
- **Uvicorn** - ASGI server

## Contributing

This is a learning project, but if you spot issues or have suggestions:
1. Open an issue describing the problem/suggestion
2. Include test cases if applicable
3. PRs welcome for bug fixes or additional status code scenarios

## What's Next

This API demonstrates the basics. Future enhancements could include:
- Authentication (401 vs 403)
- Pagination (GET /products with limit/offset)
- Bulk operations (207 Multi-Status)
- Webhooks (async patterns, 502 Bad Gateway)
- Database integration (PostgreSQL, proper connection pooling)

## License

MIT License - feel free to use this for learning or teaching.

## Blog Post

Read the full story of building this API: [Building Better Error Responses for SaaS](https://echetotech.com)

## Author

**Berner** - Support Engineering Manager  
- Blog: [EchetoTech.com](https://echetotech.com)
- GitHub: [@elchicha](https://github.com/elchicha)

Built with curiosity and caffeine. ☕