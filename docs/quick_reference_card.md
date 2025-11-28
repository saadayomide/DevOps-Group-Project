# ShopSmart - Quick Reference Card

## Fast Setup (5 Steps)

1. Setup Azure Resources
````bash
chmod +x setup-azure.sh
./setup-azure.sh
# Save the Web App name from output
````

2. Create Service Connection
Azure DevOps → Project Settings → Service Connections
New → Azure Resource Manager
Name: BCSAI2025-DEVOPS-STUDENTS-A
Select subscription & resource group

3. Update Pipeline Config
Edit azure-pipelines.yml:
````bash
variables:
  azureSubscription: 'BCSAI2025-DEVOPS-STUDENTS-A'
  appServiceName: 'your-web-app-name'  # From step 1
````

4. Push to repository
````bash
git add .
git commit -m "Setup CI/CD pipeline"
git push origin main
````

5. Create Pipeline
Azure DevOps → Pipelines → New
Select repo → Existing YAML
Choose azure-pipelines.yml → Run


## Required files in the repository
````bash
shopsmart/
├── azure-pipelines.yml          # CI/CD pipeline
├── main.py                       # FastAPI application
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation
├── tests/
│   ├── __init__.py
│   └── test_integration.py      # Integration tests
└── ShopSmart.postman_collection.json  # Postman tests
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

# Run app locally
uvicorn main:app --reload --port 8000
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


## Pipeline stages
1. BUILD      → Install dependencies, create artifact
2. LINT       → Flake8, Black formatting checks
3. TEST       → Pytest with coverage (>80%)
4. PUBLISH    → Prepare deployment package
5. DEPLOY     → Deploy to Azure App Service

Trigger: Push to main or develop branch
Duration: ~3-5 minutes
Required: All stages must pass
