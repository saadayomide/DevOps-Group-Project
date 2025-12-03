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
- Docker and Docker Compose (for PostgreSQL setup)
- pip or poetry

### PostgreSQL Setup with Docker

The easiest way to set up PostgreSQL for local development is using Docker:

#### Option 1: Using Docker Compose (Recommended)

1. **Create a `docker-compose.yml` file** in the project root:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: shopsmart-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: product_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

2. **Start PostgreSQL**:
```bash
docker-compose up -d
```

3. **Verify it's running**:
```bash
docker-compose ps
# Should show postgres service as "Up (healthy)"
```

4. **Check logs** (if needed):
```bash
docker-compose logs postgres
```

5. **Stop PostgreSQL** (when done):
```bash
docker-compose down
# To also remove the data volume: docker-compose down -v
```

#### Option 2: Using Docker Run

```bash
# Start PostgreSQL container
docker run -d \
  --name shopsmart-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=product_db \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Check if it's running
docker ps | grep shopsmart-postgres

# Stop the container
docker stop shopsmart-postgres

# Remove the container (data persists in volume)
docker rm shopsmart-postgres
```

#### Database Migrations

After PostgreSQL is running, apply database migrations:

```bash
# Set connection string
export SQL_CONNECTION_STRING="postgresql://postgres:postgres@localhost:5432/product_db"

# Run migrations
cd api
alembic upgrade head

# Seed initial data (optional)
# psql -h localhost -U postgres -d product_db -f ../db/seed_data.sql
```

### Installation

1. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Or using pyproject.toml:
```bash
pip install -e .
pip install -e ".[dev]"  # For development dependencies
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

For Docker PostgreSQL setup, your `.env` should contain:
```bash
SQL_CONNECTION_STRING=postgresql://postgres:postgres@localhost:5432/product_db
APP_ENV=development
```

4. **Set up the database** (if not using migrations):
```bash
# Make sure PostgreSQL is running (via Docker)
# The application will attempt to run migrations on startup
# Or run manually: alembic upgrade head
```

5. **Run the application**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Troubleshooting Docker PostgreSQL

**Connection refused error:**
- Ensure Docker container is running: `docker-compose ps` or `docker ps`
- Check if port 5432 is already in use: `lsof -i :5432` (macOS/Linux)
- Verify connection string matches Docker setup

**Container won't start:**
- Check logs: `docker-compose logs postgres`
- Ensure port 5432 is not used by another PostgreSQL instance
- Try removing and recreating: `docker-compose down -v && docker-compose up -d`

**Reset database:**
```bash
# Stop and remove container with data
docker-compose down -v

# Start fresh
docker-compose up -d

# Re-run migrations
alembic upgrade head
```

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

### Catalog API (product categories)
The catalog API provides static metadata about product categories so the frontend can build structured shopping-list items (instead of free-text).

**Base path:** `/api/v1/catalog`

#### GET `/catalog/categories`
Returns a list of available categories.

**Response 200 (example)**
```json
[
  {
    "code": "milk",
    "label": "Leche"
  },
  {
    "code": "eggs",
    "label": "Huevos"
  },
  {
    "code": "bread",
    "label": "Pan"
  }
]
```

Each element is a CategorySummary:
- `code`: internal code to be used in the shopping list payload (e.g. "milk").
- `label`: human-friendly label to display in the UI (e.g. "Leche").

#### GET `/catalog/categories/{code}`
Returns full details for a single category.

**Response 200 (example for milk)**
```json
{
  "code": "milk",
  "label": "Leche",
  "units": ["unit", "L"],
  "variants": ["entera", "semidesnatada", "desnatada", "sin lactosa"],
  "brands": ["Hacendado", "Carrefour", "Alcampo", "Ahorramás", "El Corte Inglés", "Mercadona"]
}
```

If the category does not exist:

**Response 404**
```json
{
  "detail": "Unknown category"
}
```

This is used by the frontend to:
- Build the shopping list item form (fields like brand, variants, unit).
- Ensure the payload uses a known category code and valid unit/variants.

## Shopping list item shape (planned for next sprint)
The frontend should **not** send free-text items. Instead, each line in the shopping list will be a structured object built from the catalog.

Planned shape for each item:
```json
{
  "category": "milk",            // from GET /catalog/categories
  "brand": "Hacendado",          // one of category.brands, or null
  "variants": ["desnatada"],     // subset of category.variants
  "quantity": 3.0,
  "unit": "unit"                 // one of category.units, e.g. "unit" or "L"
}
```

Planned request for creating a shopping list:
```json
{
  "name": "Compra fin de semana",
  "items": [
    {
      "category": "milk",
      "brand": "Hacendado",
      "variants": ["desnatada"],
      "quantity": 3,
      "unit": "unit"
    },
    {
      "category": "eggs",
      "brand": null,
      "variants": ["L"],
      "quantity": 12,
      "unit": "unit"
    }
  ]
}
```

This will be handled by `POST /api/v1/shopping-lists` in the next sprint.

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
