# Unit Testing Documentation

## Overview
Comprehensive unit tests for the FastAPI application using pytest and httpx TestClient.

## Test Infrastructure

### Test Database
- Uses SQLite in-memory database (`sqlite:///:memory:`) for fast, isolated tests
- Each test function gets a fresh database with tables created automatically
- Test data is seeded via `seed_test_data` fixture (3 products × 3 stores)

### Fixtures (`tests/conftest.py`)
- `test_db`: Creates a test database session with tables
- `test_client`: Creates a FastAPI TestClient with database dependency override
- `seed_test_data`: Seeds test database with sample data (3 products, 3 stores, 9 prices)

### Test Structure
```
tests/
├── conftest.py                    # Test fixtures and configuration
├── unit/
│   ├── test_compare_service.py          # Service helper method tests
│   ├── test_compare_service_integration.py  # compare_basket() integration tests
│   ├── test_compare_route.py            # Compare endpoint HTTP tests
│   ├── test_normalization.py            # Normalization service tests
│   └── test_routes.py                   # Other route tests (products, supermarkets, prices)
└── integration/
    └── test_api.py                      # Integration tests
```

## Required Test Cases

### ✅ 1. Picks Global Min When All Stores Have Prices
**File**: `tests/unit/test_compare_service_integration.py::TestCompareBasket::test_picks_global_min_when_all_stores_have_prices`

**Test**: Verifies that when all products exist at all stores, the algorithm picks the cheapest price for each item.

**Expected Behavior**:
- Milk: Target ($2.49) - cheapest
- Bread: Kroger ($1.89) - cheapest  
- Eggs: Target ($3.29) - cheapest

### ✅ 2. Returns Unmatched If Product Doesn't Exist
**File**: `tests/unit/test_compare_service_integration.py::TestCompareBasket::test_returns_unmatched_if_product_doesnt_exist`

**Test**: Verifies that products not found in database are added to `unmatched` list.

### ✅ 3. Tie Resolved By Running Store Totals
**File**: `tests/unit/test_compare_service_integration.py::TestCompareBasket::test_tie_resolved_by_running_store_totals`

**Test**: Verifies that when two stores have the same price, the store with lower current basket subtotal is chosen (minimizes store switches).

### ✅ 4. Empty Items → 400 BadRequest
**File**: `tests/unit/test_compare_route.py::TestCompareRoute::test_empty_items_returns_400`

**Test**: Verifies that empty items list returns 400 BadRequest with error message.

### ✅ 5. Unknown Stores → Ignored Silently
**File**: `tests/unit/test_compare_service_integration.py::TestCompareBasket::test_unknown_stores_ignored_silently`

**Test**: Verifies that unknown stores are ignored and comparison proceeds with known stores only.

## Test Coverage

### Current Coverage
- **Service Layer**: ~61% (compare_service.py)
- **Routes**: ~33-52% (varies by route)
- **Overall**: ~65% (target: ≥80%)

### Coverage Targets
- **Service Layer**: ≥80%
- **Routes**: ≥80%
- **Overall**: ≥80%

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test
```bash
pytest tests/unit/test_compare_service_integration.py::TestCompareBasket::test_picks_global_min_when_all_stores_have_prices -v
```

### Run Tests for Specific Module
```bash
pytest tests/unit/test_compare_service_integration.py -v
```

## Test Data

### Seeded Data (3 products × 3 stores)
- **Products**: Milk, Bread, Eggs
- **Stores**: Walmart, Target, Kroger
- **Prices**:
  - Milk: Walmart $2.99, Target $2.49, Kroger $2.79
  - Bread: Walmart $1.99, Target $2.19, Kroger $1.89
  - Eggs: Walmart $3.49, Target $3.29, Kroger $3.69

## Test Categories

### Unit Tests (Service Layer)
- `test_compare_service.py`: Tests helper methods (find_cheapest, find_most_expensive, etc.)
- `test_compare_service_integration.py`: Tests `compare_basket()` with database
- `test_normalization.py`: Tests normalization functions

### Integration Tests (Routes)
- `test_compare_route.py`: Tests POST /api/v1/compare endpoint
- `test_routes.py`: Tests GET endpoints for products, supermarkets, prices

## Known Issues

1. Some route tests need `test_db` fixture to ensure tables are created
2. Coverage is below 80% target - needs additional tests for edge cases
3. Error response format tests need to verify JSON structure

## Future Improvements

1. Add more edge case tests
2. Add performance tests for large datasets
3. Add tests for error scenarios
4. Increase coverage to ≥80%
5. Add tests for middleware and error handlers

