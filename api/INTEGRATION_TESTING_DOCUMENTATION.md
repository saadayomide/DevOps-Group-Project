# Integration Testing Documentation

## Overview
Integration tests for the FastAPI Product Comparison API using Postman collections and pytest. These tests can be used in CI/CD pipelines and smoke tests.

## Postman Collection

### File
- `postman_collection.json` - Postman collection with all integration tests

### Usage

#### Import into Postman
1. Open Postman
2. Click "Import" button
3. Select `postman_collection.json`
4. Import the environment file (`postman_environment.json`) if needed

#### Run Collection
1. Select the collection
2. Click "Run" button
3. Configure base URL in environment variable `base_url` (default: `http://localhost:8000`)
4. Click "Run" to execute all tests

#### Run in CI/CD Pipeline
Postman collections can be run using Newman (Postman CLI):

```bash
# Install Newman
npm install -g newman

# Run collection
newman run postman_collection.json \
  --environment postman_environment.json \
  --env-var "base_url=http://your-api-url:8000"

# With HTML report
newman run postman_collection.json \
  --environment postman_environment.json \
  --env-var "base_url=http://your-api-url:8000" \
  --reporters html \
  --reporter-html-export report.html
```

### Test Cases in Collection

#### 1. Health Check
- **Endpoint**: `GET /health`
- **Test**: Verifies status code 200 and response has `status: "ok"`

#### 2. GET /products
- **Endpoint**: `GET /api/v1/products/`
- **Test**: 
  - Status code 200
  - Response is an array
  - **Returns more than 0 rows** (required for integration test)
  - Each product has `id` and `name`

#### 3. POST /compare - 3 items
- **Endpoint**: `POST /api/v1/compare`
- **Request Body**:
  ```json
  {
    "items": ["Milk", "Bread", "Eggs"],
    "stores": ["Walmart", "Target", "Kroger"]
  }
  ```
- **Tests**:
  - Status code 200
  - Response has required fields: `items`, `storeTotals`, `overallTotal`, `unmatched`
  - Items array has correct structure (name, store, price)
  - StoreTotals array has correct structure (store, total)
  - **Returns correct mapping for 3 items**
  - **Store totals match requested stores**
  - **Totals are calculated correctly**

#### 4. Error Handling
- **Endpoint**: `POST /api/v1/compare` with empty items
- **Test**: Verifies 400 BadRequest with proper error format

## Pytest Integration Tests

### File
- `tests/integration/test_api_integration.py` - Pytest integration tests

### Usage

#### Run Integration Tests
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test
pytest tests/integration/test_api_integration.py::TestAPIIntegration::test_post_compare_with_3_items_returns_correct_mapping_and_totals -v
```

#### Run in CI/CD Pipeline
```bash
# With coverage
pytest tests/integration/ --cov=app --cov-report=term

# With HTML report
pytest tests/integration/ --html=report.html --self-contained-html
```

### Test Cases

#### 1. `test_get_products_returns_more_than_zero_rows`
- **Requirement**: GET /products returns >0 rows
- **Verifies**:
  - Status code 200
  - Response is a list
  - List length > 0
  - Each product has `id` and `name`

#### 2. `test_post_compare_with_3_items_returns_correct_mapping_and_totals`
- **Requirement**: POST /compare with 3 items returns correct mapping & totals
- **Verifies**:
  - Status code 200
  - Response structure (items, storeTotals, overallTotal, unmatched)
  - Items have correct structure (name, store, price)
  - Store totals match requested stores
  - Totals are calculated correctly
  - Overall total is reasonable

#### 3. `test_post_compare_with_3_items_handles_unmatched`
- **Additional Test**: Verifies unmatched items are handled correctly

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run integration tests
        run: |
          pytest tests/integration/ -v
      
      - name: Run Postman tests with Newman
        run: |
          npm install -g newman
          newman run postman_collection.json \
            --env-var "base_url=http://localhost:8000"
```

### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    
    stages {
        stage('Integration Tests') {
            steps {
                sh 'pytest tests/integration/ -v'
                sh 'newman run postman_collection.json --env-var "base_url=http://localhost:8000"'
            }
        }
    }
}
```

## Smoke Tests

These integration tests can be used as smoke tests to verify the API is working after deployment:

### Quick Smoke Test
```bash
# Health check
curl http://localhost:8000/health

# Products endpoint
curl http://localhost:8000/api/v1/products/ | jq 'length > 0'

# Compare endpoint
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" \
  -d '{"items": ["Milk", "Bread", "Eggs"], "stores": ["Walmart", "Target", "Kroger"]}' \
  | jq '.items | length > 0'
```

## Environment Variables

### Postman Environment
- `base_url`: Base URL for the API (default: `http://localhost:8000`)

### Pytest Environment
Tests use the test database fixture from `conftest.py` which sets:
- `SQL_CONNECTION_STRING=sqlite:///:memory:`
- `APP_ENV=test`

## Test Data Requirements

For integration tests to pass, the database must have:
- At least 1 product
- At least 2 supermarkets/stores
- At least 1 price entry

The test fixtures (`seed_test_data`) provide:
- 3 products (Milk, Bread, Eggs)
- 3 supermarkets (Walmart, Target, Kroger)
- 9 prices (3 products × 3 stores)

## Troubleshooting

### Postman Tests Failing
1. Verify `base_url` environment variable is set correctly
2. Ensure API is running and accessible
3. Check that database has required test data
4. Verify network connectivity

### Pytest Tests Failing
1. Ensure test database is properly set up
2. Check that `seed_test_data` fixture is being used
3. Verify SQLite is available (for in-memory database)
4. Check test logs for specific error messages

## Team C Usage

Team C can use these tests in their pipeline:

1. **Postman Collection**: Import `postman_collection.json` and run with Newman
2. **Pytest Tests**: Run `pytest tests/integration/` in CI/CD pipeline
3. **Smoke Tests**: Use the quick smoke test commands after deployment

Both approaches verify:
- ✅ GET /products returns >0 rows
- ✅ POST /compare with 3 items returns correct mapping & totals

