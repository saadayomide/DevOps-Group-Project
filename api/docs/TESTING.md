# Testing & Validation Guide

## Fixtures & Test Infrastructure
- **SQLite in-memory DB** (`sqlite:///:memory:`) powers deterministic, isolated tests.
- **Fixtures (`tests/conftest.py`)**
  - `test_db`: creates/drops tables per test, yields SQLAlchemy session.
  - `test_client`: FastAPI `TestClient` wired to the test session via dependency override.
  - `seed_test_data`: seeds 3 products × 3 supermarkets × 9 prices (Milk, Bread, Eggs × Walmart/Target/Kroger).
- **Directory layout**
```
tests/
├── unit/
│   ├── test_compare_service.py            # Helper utilities
│   ├── test_compare_service_integration.py# compare_basket + DB
│   ├── test_compare_route.py              # POST /compare
│   ├── test_routes.py                     # Products/Supermarkets/Prices
│   └── test_normalization.py              # Synonyms + normalization
└── integration/
    ├── test_api_integration.py            # End-to-end flows (reuse fixtures)
    └── test_api.py                        # Legacy/TestClient checks
```

## Core Test Cases (Definition of Done)
1. **Global minimum selection** – ensures `/compare` picks cheapest price when every store stocks an item.
2. **Unmatched products** – missing items land in `unmatched` array.
3. **Tie-breaking** – equal prices resolved via running store totals (minimizes store hopping).
4. **Empty items/stores** – route returns 400 BadRequest with structured error.
5. **Unknown stores** – ignored gracefully; comparison proceeds with known stores only.

See `tests/unit/test_compare_service_integration.py` and `tests/unit/test_compare_route.py` for reference implementations.

## Running Pytest
```bash
# All tests with verbose output
pytest tests/ -v

# Unit or integration subsets
pytest tests/unit -v
pytest tests/integration -v

# Coverage
pytest tests/ --cov=app --cov-report=term --cov-report=html
```

### Helpful targets
```bash
# Single test case
pytest tests/unit/test_compare_service_integration.py::TestCompareBasket::test_picks_global_min_when_all_stores_have_prices -v

# Generate HTML coverage under htmlcov/
pytest --cov=app --cov-report=html
```

## Integration Tests (Pytest)
`tests/integration/test_api_integration.py` exercises real request/response flows:
- `GET /api/v1/products` must return > 0 rows once seed data is loaded.
- `POST /api/v1/compare` with three items validates:
  - Response structure (`items`, `storeTotals`, `overallTotal`, `unmatched`).
  - Store totals align with requested stores.
  - Totals are arithmetically correct (tolerance ±0.01).
- Additional checks ensure supermarkets/prices endpoints emit data and unmatched items behave correctly.

## Postman / Newman Collection
- **Collection**: `postman_collection.json`
- **Environment (optional)**: `postman_environment.json`
- **Folders & Highlights**:
  1. **Health Check** – verifies `/health`.
  2. **Products** – `GET /api/v1/products/` ensures >0 rows and captures sample IDs.
  3. **Supermarkets** – lists stores and stores names for reuse.
  4. **Compare** – posts the canonical 3-item payload plus error-path test (empty items → 400).
- **Base URL** set via environment variable `base_url` (defaults to `http://localhost:8000`).

### Running via Postman UI
1. Import `postman_collection.json` (and `postman_environment.json` if desired).
2. Set `base_url` in the environment.
3. Click **Run** on the collection to execute smoke tests end-to-end.

### Running via Newman (CI/CD friendly)
```bash
npm install -g newman
newman run postman_collection.json --env-var "base_url=http://localhost:8000"

# With reports
newman run postman_collection.json \
  --env-var "base_url=http://localhost:8000" \
  --reporters cli,html \
  --reporter-html-export postman-report.html
```

## CI/CD Examples
```yaml
# GitHub Actions
- name: Install deps
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-cov
- name: Run tests
  run: pytest tests/ -v --cov=app
- name: Run Postman collection
  run: |
    npm install -g newman
    nnewman run postman_collection.json --env-var "base_url=http://127.0.0.1:8000"
```

```groovy
// Jenkins declarative pipeline
pipeline {
  stages {
    stage('Test') {
      steps {
        sh 'pytest tests/ -v'
        sh 'nnewman run postman_collection.json --env-var "base_url=http://localhost:8000"'
      }
    }
  }
}
```

## Smoke Test Snippets
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/products/ | jq 'length > 0'
curl -X POST http://localhost:8000/api/v1/compare \
  -H 'Content-Type: application/json' \
  -d '{"items":["Milk","Bread","Eggs"],"stores":["Walmart","Target","Kroger"]}' \
  | jq '.items | length > 0'
```

## Future Improvements
- Raise coverage ≥80% (focus on route edge cases + middleware).
- Add performance/regression suites with larger datasets.
- Extend Postman/Newman scripts with environment-specific data loaders.
