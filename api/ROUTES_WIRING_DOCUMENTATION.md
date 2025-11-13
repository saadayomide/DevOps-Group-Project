# Routes Wiring Documentation

## Overview
This document describes how routes are wired to use services and database sessions.

## Route Architecture

### 1. Compare Route (`routes/compare.py`)

**Endpoint**: `POST /api/v1/compare`

**Implementation**:
- Uses `CompareRequest` schema for request validation
- Calls `compare_service.compare_basket(request, db)` to perform the comparison
- All business logic is in the service layer
- Route handles validation (empty items/stores) and logging only

**Code Structure**:
```python
@router.post("/", response_model=CompareResponse)
async def compare_items(
    request: CompareRequest = Body(...),
    db: Session = Depends(get_db)
):
    # Validate request
    if not request.items:
        raise HTTPException(...)
    
    # Call service
    response = compare_service.compare_basket(request, db)
    
    # Log operation
    logger.info(...)
    
    return response
```

**Service Method**: `compare_service.compare_basket(request, db)`
- Takes `CompareRequest` and `Session` as parameters
- Handles all database queries and business logic
- Returns `CompareResponse`

### 2. Products Route (`routes/products.py`)

**Endpoints**:
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{product_id}` - Get product by ID
- `POST /api/v1/products` - Create product
- `PUT /api/v1/products/{product_id}` - Update product
- `DELETE /api/v1/products/{product_id}` - Delete product

**Implementation**:
- All endpoints use `db: Session = Depends(get_db)`
- Direct database queries via `db.query(Product)`
- No service layer (simple CRUD operations)

**Example**:
```python
@router.get("/", response_model=List[ProductResponse])
async def get_products(
    q: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    # ... filtering logic
    products = query.all()
    return [ProductResponse(id=p.id, name=p.name) for p in products]
```

### 3. Supermarkets Route (`routes/supermarkets.py`)

**Endpoints**:
- `GET /api/v1/supermarkets` - List supermarkets
- `GET /api/v1/supermarkets/{supermarket_id}` - Get supermarket by ID
- `POST /api/v1/supermarkets` - Create supermarket
- `PUT /api/v1/supermarkets/{supermarket_id}` - Update supermarket
- `DELETE /api/v1/supermarkets/{supermarket_id}` - Delete supermarket

**Implementation**:
- All endpoints use `db: Session = Depends(get_db)`
- Direct database queries via `db.query(Supermarket)`
- No service layer (simple CRUD operations)

**Example**:
```python
@router.get("/", response_model=List[SupermarketResponse])
async def get_supermarkets(
    db: Session = Depends(get_db)
):
    supermarkets = db.query(Supermarket).all()
    return [SupermarketResponse(id=s.id, name=s.name) for s in supermarkets]
```

### 4. Prices Route (`routes/prices.py`)

**Endpoints**:
- `GET /api/v1/prices` - List prices (with optional filters)
- `GET /api/v1/prices/{price_id}` - Get price by ID
- `POST /api/v1/prices` - Create price
- `PUT /api/v1/prices/{price_id}` - Update price
- `DELETE /api/v1/prices/{price_id}` - Delete price

**Implementation**:
- All endpoints use `db: Session = Depends(get_db)`
- Direct database queries via `db.query(Price)`
- Validates foreign key relationships (product_id, store_id)
- No service layer (simple CRUD operations)

**Example**:
```python
@router.get("/", response_model=List[PriceSchema])
async def get_prices(
    productId: Optional[int] = Query(None),
    storeId: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Price)
    if productId is not None:
        query = query.filter(Price.product_id == productId)
    if storeId is not None:
        query = query.filter(Price.store_id == storeId)
    return query.all()
```

## Database Session Management

### Session Dependency Injection
All routes use FastAPI's dependency injection to get database sessions:

```python
from app.db import get_db
from sqlalchemy.orm import Session

@router.get("/")
async def some_endpoint(
    db: Session = Depends(get_db)
):
    # Use db session for queries
    result = db.query(Model).all()
    return result
```

### Session Lifecycle
- Sessions are created per request via `get_db()` dependency
- Sessions are automatically closed after request completion
- Transactions are committed automatically for write operations
- Errors trigger automatic rollback

## Service Layer Pattern

### When to Use Services
- **Complex business logic**: Use service layer (e.g., `compare_basket`)
- **Simple CRUD**: Direct database queries in routes (e.g., products, supermarkets, prices)

### Compare Service Example
The compare route uses a service because it involves:
- Complex normalization logic
- Multiple database queries
- Business rules (tie-breaking, price selection)
- Response aggregation

### Direct DB Access Example
Simple CRUD routes access the database directly because they:
- Perform simple queries
- Have minimal business logic
- Follow standard REST patterns

## Summary

| Route | Service Layer | DB Access |
|-------|--------------|-----------|
| `/compare` | ✅ `compare_service.compare_basket()` | Via service |
| `/products` | ❌ Direct queries | `db.query(Product)` |
| `/supermarkets` | ❌ Direct queries | `db.query(Supermarket)` |
| `/prices` | ❌ Direct queries | `db.query(Price)` |

All routes properly use `db: Session = Depends(get_db)` for database access.

