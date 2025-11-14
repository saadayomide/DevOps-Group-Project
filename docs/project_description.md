# ShopSmart - Smart Shopping List Optimizer

Automatically find the cheapest combination of supermarkets for your shopping list

## Table of Contents
1. Overview
2. Features
3. Architecture
4. Getting Started
5. CI/CD Pipeline
6. API Documentation
7. Testing

## Overview
ShopSmart helps consumers save money by analyzing prices from multiple supermarkets and suggesting where to buy each item to minimize total cost. No more manual price comparisons or wasted time - just enter your shopping list and let ShopSmart optimize your shopping route.

### Problem
Grocery prices vary widely across supermarkets
Consumers waste time comparing prices manually
No unified tool that optimizes shopping routes across stores

### Solution
Single web app where users input shopping lists and select supermarkets
Backend analyzes price data and suggests optimal product-to-store mapping
Real-time price comparison with detailed savings breakdown


## MVP Features 
1. Shopping List Management
  - Create and manage shopping lists
  - Add/remove items from list
  - Case-insensitive product search

2. Supermarket Selection
  - View available supermarkets (Mercadona, Carrefour, Lidl)
  - Select multiple stores to compare
  - Dynamic store selection

3. Price Comparison
  - Real-time price comparison across stores
  - Detailed results with cheapest store per product
  - Total cost calculation and savings breakdown
  - Handle missing products gracefully

4. Backend & DevOps
  - FastAPI REST API with full documentation
  - Azure SQL Database integration (mock data for MVP)
  - Automated CI/CD pipeline (Build → Lint → Test → Deploy)
  - Application Insights monitoring
  - Health checks and error handling


## Architecture
┌─────────────────┐
│   Frontend UI   │
│  (React/HTML)   │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────────────────────┐
│     FastAPI Backend API         │
│  ┌──────────────────────────┐  │
│  │  /api/compare            │  │
│  │  /api/products           │  │
│  │  /api/supermarkets       │  │
│  │  /health                 │  │
│  └──────────────────────────┘  │
└────────┬────────────────────────┘
         │
         │ SQLAlchemy ORM
         │
┌────────▼────────────────────────┐
│    Azure SQL Database           │
│  ┌──────────────────────────┐  │
│  │  Products Table          │  │
│  │  Supermarkets Table      │  │
│  │  Prices Table            │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘

         │ Telemetry
         │
┌────────▼────────────────────────┐
│  Application Insights           │
│  - Request tracking             │
│  - Performance metrics          │
│  - Error logging                │
└─────────────────────────────────┘


## Getting Started
1. Prerequisites
  - Python 3.11 or higher
  - pip (Python package manager)
  - Git
  - Azure account (for deployment)

2. Local Development Setup
  a. Clone the repository
````bash
  git clone https://github.com/saadayomide/DevOps-Group-Project.git
  cd shopsmart
````

  b. Create virtual environment
````bash
  python -m venv venv

  # On Windows
  venv\Scripts\activate

  # On macOS/Linux
  source venv/bin/activate
````

  c. Install dependencies
````bash
  pip install -r requirements.txt
````

  d. Run the application
````bash
  # Development server with auto-reload
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
````

  e. Access the API
    - API Documentation: http://localhost:8000/docs
    - Alternative Docs: http://localhost:8000/redoc
    - Health Check: http://localhost:8000/health


## CI/CD Pipeline
1. Pipeline Architecture
Our automated CI/CD pipeline consists of 5 stages:
┌─────────┐    ┌──────┐    ┌──────┐    ┌─────────┐    ┌────────┐
│  Build  │ -> │ Lint │ -> │ Test │ -> │ Publish │ -> │ Deploy │
└─────────┘    └──────┘    └──────┘    └─────────┘    └────────┘

2. Stage Details
  a. Build Stage
  - Install Python 3.11
  - Install all dependencies from requirements.txt
  - Package application files
  - Create build artifact

  b. Lint Stage
  - Flake8: Python code linting (PEP 8 compliance)
  - Black: Code formatting checks
  - Pylint: Static code analysis
  - Runs in parallel after build

  c. Test Stage
  - Run unit tests with pytest
  - Generate code coverage reports (target: >80%)
  - Publish test results to Azure DevOps
  - Integration tests for all API endpoints
  - Performance tests

  d. Publish Artifact Stage
  - Verify build artifact integrity
  - Prepare deployment package
  - Store artifacts for deployment

  e. Deploy Staging Stage
  - Deploy to Azure App Service (Linux)
  - Configure environment variables
  - Start application with uvicorn
  - Smoke tests on staging environment

3. Pipeline Triggers
  - Automatic: Triggers on push to main or develop branches
  - Pull Request: Validates all PRs before merge
  - Manual: Can be triggered from Azure DevOps UI

4. Pipeline Configuration
The pipeline is defined in azure-pipelines.yml. Key variables:
````yaml
variables:
  pythonVersion: '3.11'
  azureSubscription: 'BCSAI2025-DEVOPS-STUDENTS-A'
  appServiceName: 'shopsmart-backend-staging'
````


## API Documentation
1. Base URL
  - Local: http://localhost:8000
  - Staging: https://shopsmart-backend-staging.azurewebsites.net

2. Endpoints
  a. Health & Info
GET /
Root endpoint with API information
````json
{
  "message": "Welcome to ShopSmart API",
  "version": "1.0.0",
  "endpoints": {...}
}
````

GET /health
Health check for monitoring
````json
{
  "status": "healthy",
  "service": "ShopSmart API",
  "version": "1.0.0"
}
````

  b. Data Endpoints
GET /api/supermarkets
Get all available supermarkets
````json
[
  {
    "id": 1,
    "name": "Mercadona",
    "location": "Spain"
  },
  ...
]
````

GET /api/products
Get all available products
````json
[
  {
    "id": 1,
    "name": "milk",
    "category": "dairy"
  },
  ...
]
````

GET /api/prices
Get all price data (for debugging)

  c. Price Comparison
POST /api/compare
Compare prices across selected supermarkets
Request:
````json
{
  "items": ["milk", "bread", "eggs"],
  "stores": ["Mercadona", "Carrefour", "Lidl"]
}
````

Response:
````json
{
  "recommendations": [
    {
      "product": "milk",
      "cheapest_store": "Lidl",
      "price": 1.15,
      "all_prices": {
        "Mercadona": 1.20,
        "Carrefour": 1.35,
        "Lidl": 1.15
      }
    },
    ...
  ],
  "total_cost": 4.30,
  "savings": 0.45,
  "store_totals": {
    "Lidl": 2.00,
    "Mercadona": 2.30
  }
}
````

3. Interactive Documentation
FastAPI provides automatic interactive documentation:
  - Swagger UI: /docs - Try out all endpoints with a user-friendly interface
  - ReDoc: /redoc - Alternative documentation format


## Testing
1. Running Tests Locally
````bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# View coverage report
# Open htmlcov/index.html in browser

# Run specific test file
pytest tests/test_integration.py

# Run specific test class
pytest tests/test_integration.py::TestCompareEndpoint
````

2. Test structure
tests/
├── __init__.py
├── test_integration.py      # API endpoint integration tests
├── test_unit.py              # Unit tests for business logic
└── test_performance.py       # Performance and load tests

3. Test Coverage
Current test coverage: 85%+
Covered areas:
  - All API endpoints
  - Price comparison logic
  - Error handling
  - Data validation
  - Edge cases

4. Integration Tests with Postman
Import ShopSmart.postman_collection.json into Postman:
  a. Open Postman
  b. Click Import → Upload File
  c. Select ShopSmart.postman_collection.json
  d. Set environment variables:
  - base_url: http://localhost:8000
  - staging_url: your Azure staging URL
Run the entire collection or individual requests.
