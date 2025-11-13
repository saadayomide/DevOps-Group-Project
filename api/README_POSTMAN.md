# Postman Collection - Quick Start Guide

## Files
- `postman_collection.json` - Postman collection with integration tests
- `postman_environment.json` - Environment variables for Postman

## Quick Start

### 1. Import into Postman
1. Open Postman
2. Click **Import** button
3. Select `postman_collection.json`
4. (Optional) Import `postman_environment.json` for environment variables

### 2. Set Base URL
1. Click on **Environments** in left sidebar
2. Select or create an environment
3. Add variable: `base_url` = `http://localhost:8000` (or your API URL)

### 3. Run Tests
1. Select the collection: **FastAPI Product Comparison API**
2. Click **Run** button
3. Click **Run FastAPI Product Comparison API** to execute all tests

## Required Tests

### ✅ GET /products returns >0 rows
- **Folder**: Products → GET /products
- **Test**: Verifies response has more than 0 products
- **Assertion**: `pm.expect(jsonData.length).to.be.above(0);`

### ✅ POST /compare with 3 items returns correct mapping & totals
- **Folder**: Compare → POST /compare - 3 items
- **Request**: 
  ```json
  {
    "items": ["Milk", "Bread", "Eggs"],
    "stores": ["Walmart", "Target", "Kroger"]
  }
  ```
- **Tests**:
  - Response has correct structure
  - Items are correctly mapped to stores
  - Store totals are calculated correctly
  - Overall total is present

## Running in CI/CD (Newman)

### Install Newman
```bash
npm install -g newman
```

### Run Collection
```bash
newman run postman_collection.json \
  --env-var "base_url=http://localhost:8000"
```

### With HTML Report
```bash
newman run postman_collection.json \
  --env-var "base_url=http://localhost:8000" \
  --reporters html \
  --reporter-html-export report.html
```

### With Environment File
```bash
newman run postman_collection.json \
  --environment postman_environment.json \
  --env-var "base_url=http://your-api-url:8000"
```

## Test Results

All tests should pass:
- ✅ Health Check
- ✅ GET /products returns >0 rows
- ✅ POST /compare with 3 items returns correct mapping & totals
- ✅ Error handling (empty items → 400)

## Troubleshooting

1. **Tests failing**: Check that `base_url` is set correctly
2. **No data returned**: Ensure database has test data (products, stores, prices)
3. **Connection errors**: Verify API is running and accessible

