# ShopSmart Deployment Guide

Complete step-by-step guide for setting up CI/CD pipeline and deploying ShopSmart to Azure.

## Prerequisites Checklist
Before starting, ensure you have:

 Azure account with active subscription (BCSAI2025-DEVOPS-STUDENTS-A)
 Azure DevOps account
 Git repository (GitHub/Azure Repos)
 Azure CLI installed locally
 Python 3.11+ installed
 Repository cloned locally

 ## Part 1: Azure Infrastructure Setup

1. Make the setup script executable
````bash
chmod +x setup-azure.sh
````

2. Run the setup script
````bash
./setup-azure.sh
````

3. Follow the prompts
The script will create all necessary resources
Save the output configuration file (azure-config.txt)
Note down the Web App name and URLs


## Part 2: Azure DevOps Pipeline Setup

1. Create Azure DevOps Project
Go to dev.azure.com
Click "New Project"
Enter project name: "ShopSmart"
Set visibility (Private recommended)
Click "Create"

2. Connect Your Repository
  a. For GitHub:
Go to Project Settings → Service Connections
Click New Service Connection
Select GitHub
Authorize Azure Pipelines to access your repository
Select your ShopSmart repository

  b. For Azure Repos:
Repository is automatically created with the project
Clone and push your code:
````bash
git remote add origin https://dev.azure.com/your-org/ShopSmart/_git/ShopSmart
git push -u origin main
````

3. Create Azure Service Connection
  a. Go to Project Settings → Service Connections
  b. Click New Service Connection
  c. Select Azure Resource Manager
  d. Choose Service Principal (automatic)
  e. Configure:
      - Subscription: Select your Azure subscription
      - Resource Group: shopsmart-rg
      - Service Connection Name: BCSAI2025-DEVOPS-STUDENTS-A
      - Description: Azure connection for ShopSmart
  f. Check "Grant access permission to all pipelines"
  g. Click Save

4. Add Pipeline Files to Repository
  a. Copy pipeline file to your repository root: azure-pipelines.yml (provided in artifacts)
  b. Update variables in azure-pipelines.yml:
  ````yaml
  variables:
  pythonVersion: '3.11'
  azureSubscription: 'BCSAI2025-DEVOPS-STUDENTS-A'  # Your service connection name
  appServiceName: 'shopsmart-backend-staging'        # Your Web App name
  buildArtifact: 'shopsmart-drop'
  ````
  c. Add other files to repository:
      - requirements.txt
      - main.py
      - tests/test_integration.py
      - README.md
  d. Commit and push:
  ````bash
  git add .
  git commit -m "Add CI/CD pipeline configuration"
  git push origin main
  ````
  e. Create Pipeline in Azure DevOps:
      i. Go to Pipelines → Pipelines
      ii. Click New Pipeline
      iii. Select your repository location (GitHub/Azure Repos)
      iv. Select your repository
      v. Choose Existing Azure Pipelines YAML file
      vi. Select /azure-pipelines.yml
      vii. Click Continue
      viii. Review the pipeline
      ix. Click Run
  f. Create Environment:
      i. Go to Pipelines → Environments
      ii. Click New Environment
      iii. Name: staging
      iv. Description: "Staging environment for ShopSmart"
      v. Click Create


## Part 3: Verification & Testing

1. Verify Pipeline Execution:
Watch the pipeline run through all stages:
  - Build (Install dependencies, package app)
  - Lint (Code quality checks)
  - Test (Run tests with coverage)
  - Publish Artifact (Prepare deployment)
  - Deploy Staging (Deploy to Azure)

2. Check Deployment
Visit your Web App URL:
````bash
https://your-app-name.azurewebsites.net
````
Test endpoints:
````bash
# Health check
curl https://your-app-name.azurewebsites.net/health

# Get supermarkets
curl https://your-app-name.azurewebsites.net/api/supermarkets

# API documentation
# Visit: https://your-app-name.azurewebsites.net/docs
````

3. Verify Application Insights
  a. Go to Azure Portal
  b. Navigate to Resource Group: shopsmart-rg
  c. Open shopsmart-insights
  d. Check Live Metrics
  e. Make some API requests
  f. Verify data appears in:
     - Requests
     - Performance
     - Failures
     - Metrics

4. Run Integration Tests Using Pytest
````bash
# Set environment variable
export API_BASE_URL=https://your-app-name.azurewebsites.net

# Run tests
pytest tests/test_integration.py -v
````


## Part 4: Monitoring Setup
### Create Application Insights Dashboard
1. Navigate to Application Insights
Portal → Resource Groups → shopsmart-rg → shopsmart-insights

2. Create Custom Dashboard
  a. Click "Application Dashboard" or create new
  b. Add tiles:
     - Server requests (line chart)
     - Failed requests (metric)
     - Server response time (metric)
     - Availability (availability test)

3. Pin Important Metrics
  a. Request count
  b. Average response time
  c. Failure rate
  d. Custom events

4. Set Up Alerts
  a. Response Time Alert:
  ````bash
  az monitor metrics alert create \
  --name "HighResponseTime" \
  --resource-group shopsmart-rg \
  --scopes "/subscriptions/<subscription-id>/resourceGroups/shopsmart-rg/providers/microsoft.insights/components/shopsmart-insights" \
  --condition "avg requests/duration > 2000" \
  --description "Alert when avg response time exceeds 2s"
  ````

  b. Error Rate Alert:
  ````bash
  az monitor metrics alert create \
  --name "HighErrorRate" \
  --resource-group shopsmart-rg \
  --scopes "/subscriptions/<subscription-id>/resourceGroups/shopsmart-rg/providers/microsoft.insights/components/shopsmart-insights" \
  --condition "count requests/failed > 10" \
  --description "Alert when failed requests exceed 10"
  ````
