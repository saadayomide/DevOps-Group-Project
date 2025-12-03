# ShopSmart - Quick Reference Card

## Fast Setup

1. **Azure Resources**: Create via Azure Portal or CLI (see `docs/DEVOPS_GUIDE.md`)

2. **GitHub Secrets**: Add required secrets in GitHub repository settings:
   - `AZURE_CREDENTIALS`
   - `AZURE_ACR_USERNAME`
   - `AZURE_ACR_PASSWORD`
   - `AZURE_BACKEND_STAGING_APP_NAME`
   - `AZURE_BACKEND_PRODUCTION_APP_NAME`
   - `AZURE_FRONTEND_STAGING_APP_NAME`
   - `AZURE_FRONTEND_PRODUCTION_APP_NAME`

3. **GitHub Environments**: Create `staging` and `production` environments

4. **Push to repository**: CI/CD will automatically trigger on push to `teamC2` (staging) or `main` (production)

## Project Structure
````bash
shopsmart/
├── api/                          # Backend FastAPI application
│   ├── app/                      # Application code
│   ├── tests/                    # Test suite
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Container image
├── frontend/                     # Frontend React application
│   ├── src/                      # Source code
│   ├── package.json              # Node dependencies
│   └── Dockerfile                # Container image
├── .github/workflows/            # CI/CD pipelines
│   ├── backend.yml               # Backend pipeline
│   └── frontend.yml              # Frontend pipeline
└── docs/                         # Documentation
````


## Testing commands
1. Local testing
````bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_integration.py -v

# Run app locally (from api/ directory)
cd api
uvicorn app.main:app --reload --port 8000
````

2. Test endpoints
````bash
# Health check
curl http://localhost:8000/health

# Get supermarkets
curl http://localhost:8000/api/supermarkets

# Compare prices
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"items":["milk","bread"],"stores":["Mercadona","Lidl"]}'
````


## Useful Azure CLI Commands
1. View resources
````bash
# List all resources
az resource list --resource-group shopsmart-rg --output table

# Show Web App
az webapp show --name <app-name> --resource-group shopsmart-rg
````

2. Logs and Debugging
````bash
# Stream logs
az webapp log tail --name <app-name> --resource-group shopsmart-rg

# Download logs
az webapp log download --name <app-name> --resource-group shopsmart-rg
````

3. App management
````bash
# Restart app
az webapp restart --name <app-name> --resource-group shopsmart-rg

# View settings
az webapp config appsettings list --name <app-name> --resource-group shopsmart-rg

# Update setting
az webapp config appsettings set \
  --name <app-name> \
  --resource-group shopsmart-rg \
  --settings KEY=VALUE
````


## Pipeline stages (GitHub Actions)
1. **BUILD**      → Build Docker image
2. **TEST**       → Run pytest tests (backend only)
3. **PUSH**       → Push image to Azure Container Registry
4. **DEPLOY**     → Deploy container to Azure App Service

**Trigger**: Push to `teamC2` (staging) or `main` (production)
**Duration**: ~5-10 minutes
**Required**: All stages must pass
