# Architecture & API Reference

## Overview
FastAPI application for comparing grocery prices across supermarkets. The codebase lives under `app/` and is organized into configuration, database wiring, SQLAlchemy models, Pydantic schemas, routes, and services.

```
app/
├── main.py            # FastAPI entrypoint, middleware, routers
├── config.py          # Environment-driven settings (APP_ENV, SQL_CONNECTION_STRING)
├── db.py              # SQLAlchemy engine/session factory
├── models.py          # Team A schema models (Product, Supermarket, Price)
├── schemas.py         # Pydantic schemas (CRUD + comparison)
├── routes/            # Health, products, supermarkets, prices, compare
└── services/          # compare_service + normalization helpers
```

## Application Scaffold
- **Entrypoint (`app/main.py`)**
  - Initializes FastAPI with title/version/env-driven debug flag.
  - Auto-creates tables outside the `test` environment (Alembic recommended later).
- **CORS**
  - `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`, `allow_credentials=True` (Team C will tighten later).
- **Health endpoints** (`routes/health.py`)
  - `GET /health` → `{ "status": "ok" }` (smoke tests rely on exact payload).
  - `GET /health/db` runs `SELECT 1` for DB liveness.
- **OpenAPI** available automatically at `/docs`, `/redoc`, `/openapi.json`.

## Configuration & Database Wiring
- **Settings (`config.py`)** use `pydantic-settings` v2 with `.env` support.
  - `APP_ENV` controls `settings.debug` and disables table creation in tests.
  - `SQL_CONNECTION_STRING` defaults to local Postgres; SQLite supported for tests.
- **Database (`db.py`)**
  - Conditionally enables connection pooling only for non-SQLite URLs.
  - Exposes `SessionLocal` and `get_db()` dependency for routes/services.

## Data Model & Schemas
- **SQLAlchemy Models (`models.py`)**
  - `Product(id, name, category)`
  - `Supermarket(id, name, city)`
  - `Price(id, product_id → products.id, store_id → supermarkets.id, price DECIMAL(10,2))`
  - Index on `(product_id, store_id)` supports price lookups.
- **Pydantic Schemas (`schemas.py`)**
  - CRUD schemas per entity plus lightweight response shapes (`ProductResponse`, `SupermarketResponse`).
  - Comparison contracts (single source of truth):
    - `CompareRequest { items: List[str], stores: List[str] }`
    - `CompareItem { name, store, price }`
    - `StoreTotal { store, total }`
    - `CompareResponse { items, storeTotals, overallTotal, unmatched }`

## Routes & Wiring
- **Products/Supermarkets/Prices (`routes/*.py`)**
  - Thin CRUD endpoints using `db: Session = Depends(get_db)` and direct SQLAlchemy queries.
  - GET list endpoints keep responses small (`id`, `name`) and support filters:
    - `GET /products` → optional `q`, `limit` (1–1000), `offset` (>=0).
    - `GET /prices` → optional `productId`, `storeId` (>=1).
  - FastAPI automatically returns `422` for invalid query types; explicit `404` only for missing resources.
- **Compare Route (`routes/compare.py`)**
  - Validates that `items` and `stores` are non-empty (400 on failure).
  - Delegates core logic to `CompareService.compare_basket(request, db)` and logs structured metrics (`items_requested`, `items_matched`, etc.).

## Comparison Algorithm (`services/compare_service.py`)
1. **Normalize inputs**: lower-case, trim, collapse whitespace; item synonyms handled via normalization helper.
2. **Resolve products/stores**: build maps of normalized names → DB rows (one query each).
3. **Price fetch**: single SQL query for all `(product_id, store_id)` combinations, storing minimum per pair.
4. **Cheapest selection**:
   - Iterate requested items; collect candidate stores with prices.
   - Choose minimum price; tie-break via running basket totals (keeps shopping at cheaper store).
5. **Response assembly**: `CompareResponse` containing matched items, `storeTotals`, `overallTotal` (min basket total), and `unmatched` items.

Complexity: three SQL queries (products, stores, prices) regardless of request size. Deterministic ordering and tie-breaking.

## Normalization Helpers (`services/normalization.py`)
- `normalize_item_name` → strip, lowercase, collapse whitespace, map synonyms (capsicum → bell pepper, courgette → zucchini, etc.).
- `SYNONYMS_MAP` is an in-memory dict for MVP; extend as needed.
- Shared across compare logic and testing to ensure consistent matching.

## Error Handling & Logging
- **LoggingMiddleware**
  - Logs `{ endpoint, method, status, duration_ms, error? }`, adds `X-Process-Time` header, and escalates unhandled errors.
- **Exception Handlers (`main.py`)**
  - `RequestValidationError` → 422 `{"error":"UnprocessableEntity"}`
  - `HTTPException` → type-mapped errors (400 BadRequest, 404 NotFound, etc.)
  - Catch-all → 500 InternalServerError (message redacted outside debug mode)
- **Compare Metrics**
  - `/compare` route logs counts for requested/matched/unmatched items + store count for monitoring/App Insights.

## Quick Ops Checklist
- Health check: `curl http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`
- Run server: `uvicorn app.main:app --reload`
- Key settings: `APP_ENV`, `SQL_CONNECTION_STRING`
