# FastAPI Product Comparison API

A FastAPI application for comparing product prices across different supermarkets.

## Features

- Product management
- Supermarket management
- Price tracking
- Product price comparison across supermarkets
- RESTful API with automatic documentation

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) – scaffold, configuration, models, routes, compare algorithm, normalization, and error handling.
- [`docs/TESTING.md`](docs/TESTING.md) – pytest matrix, fixtures, required comparison cases, plus Postman/Newman integration flows.
- `postman_collection.json` / `postman_environment.json` – ready-to-run smoke tests for Team C.

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL database
- pip or poetry

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using pyproject.toml:
```bash
pip install -e .
pip install -e ".[dev]"  # For development dependencies
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Set up the database:
```bash
# Make sure PostgreSQL is running
# The application will create tables automatically on first run
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Project Structure

```
api/
  app/
    __init__.py
    config.py          # Configuration settings
    db.py              # Database connection
    models.py          # SQLAlchemy models
    schemas.py         # Pydantic schemas
    routes/            # API routes
      products.py
      supermarkets.py
      prices.py
      compare.py
      health.py
    services/          # Business logic
      compare_service.py
      normalization.py
    middleware.py      # Custom middleware
    main.py            # FastAPI application
  tests/
    unit/              # Unit tests
    integration/       # Integration tests
  pyproject.toml       # Project configuration
  requirements.txt     # Python dependencies
  .env.example         # Environment variables example
```

## API Endpoints

### Health
- `GET /health` - Health check
- `GET /health/db` - Database health check

### Supermarkets
- `GET /api/v1/supermarkets/` - Get all supermarkets
- `GET /api/v1/supermarkets/{id}` - Get supermarket by ID
- `POST /api/v1/supermarkets/` - Create supermarket
- `PUT /api/v1/supermarkets/{id}` - Update supermarket
- `DELETE /api/v1/supermarkets/{id}` - Delete supermarket

### Products
- `GET /api/v1/products/` - Get all products
- `GET /api/v1/products/{id}` - Get product by ID
- `POST /api/v1/products/` - Create product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Prices
- `GET /api/v1/prices/` - Get all prices
- `GET /api/v1/prices/{id}` - Get price by ID
- `POST /api/v1/prices/` - Create price
- `PUT /api/v1/prices/{id}` - Update price
- `DELETE /api/v1/prices/{id}` - Delete price

### Compare
- `GET /api/v1/compare/?query=<product_name>` - Compare product prices
- `GET /api/v1/compare/product/{product_id}` - Compare specific product

## Testing

Run unit tests:
```bash
pytest tests/unit
```

Run integration tests:
```bash
pytest tests/integration
```

Run all tests:
```bash
pytest
```

## Development

### Code Formatting
```bash
black app tests
```

### Linting
```bash
ruff check app tests
```

### Type Checking
```bash
mypy app
```

## License

MIT

