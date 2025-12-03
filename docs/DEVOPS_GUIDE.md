# Team C - DevOps & Deployment Guide

Complete guide for Azure infrastructure, CI/CD pipelines, and deployment automation.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Azure Infrastructure Setup](#azure-infrastructure-setup)
3. [Azure DevOps Configuration](#azure-devops-configuration)
4. [CI/CD Pipeline Setup](#cicd-pipeline-setup)
5. [Containerization & ACR](#containerization--acr)
6. [CORS Configuration](#cors-configuration)
7. [Environment Variables](#environment-variables)
8. [Deployment Verification](#deployment-verification)
9. [Troubleshooting](#troubleshooting)
10. [Architecture](#architecture)

---

## Quick Start

### ✅ Pre-Deployment Checklist

- [ ] Azure subscription active
- [ ] Azure CLI installed (`az --version`)
- [ ] Azure DevOps project created
- [ ] Resource Group created (`shopsmart-rg`)
- [ ] Backend App Services created (staging + production)
- [ ] Frontend App Services created (staging + production)
- [ ] Service Connection created in Azure DevOps
- [ ] Variable Groups created (`Backend-Secrets`, `Frontend-Config`)
- [ ] Environments created (`staging`, `production`)
- [ ] Pipelines created and linked to YAML files

### 🚀 Quick Commands

```bash
# Create Backend App Services
az webapp create --resource-group shopsmart-rg --plan shopsmart-plan \
  --name shopsmart-backend-staging --runtime "PYTHON:3.11"
az webapp create --resource-group shopsmart-rg --plan shopsmart-plan \
  --name shopsmart-backend-production --runtime "PYTHON:3.11"

# Create Frontend App Services
az webapp create --resource-group shopsmart-rg --plan shopsmart-plan \
  --name shopsmart-frontend-staging --runtime "NODE:18-lts"
az webapp create --resource-group shopsmart-rg --plan shopsmart-plan \
  --name shopsmart-frontend-production --runtime "NODE:18-lts"

# Configure CORS
az webapp config appsettings set --resource-group shopsmart-rg \
  --name shopsmart-backend-staging \
  --settings CORS_ORIGINS="https://shopsmart-frontend-staging.azurewebsites.net"

# Run Smoke Tests
export BACKEND_URL=https://shopsmart-backend-staging.azurewebsites.net
./scripts/smoke-test.sh
```

---

## Azure Infrastructure Setup

### Step 1: Run Infrastructure Setup Script

```bash
chmod +x setup-azure.sh
./setup-azure.sh
```

This creates:
- Resource Group: `shopsmart-rg`
- App Service Plan: `shopsmart-plan`
- Backend App Service (Staging): `shopsmart-backend-staging`
- Application Insights: `shopsmart-insights`
- Key Vault: `shopsmart-kv-*`

### Step 2: Create Production App Service

```bash
az webapp create \
  --resource-group shopsmart-rg \
  --plan shopsmart-plan \
  --name shopsmart-backend-production \
  --runtime "PYTHON:3.11"
```

### Step 3: Create Frontend App Services

```bash
# Staging
az webapp create \
  --resource-group shopsmart-rg \
  --plan shopsmart-plan \
  --name shopsmart-frontend-staging \
  --runtime "NODE:18-lts"

# Production
az webapp create \
  --resource-group shopsmart-rg \
  --plan shopsmart-plan \
  --name shopsmart-frontend-production \
  --runtime "NODE:18-lts"
```

---

## Azure DevOps Configuration

### Step 1: Create Service Connection

1. Azure DevOps → Project Settings → Service Connections
2. New Service Connection → Azure Resource Manager
3. Service Principal (automatic)
4. Configure:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: `shopsmart-rg`
   - **Service Connection Name**: `Shop-Smart-Service`
   - ✅ Grant access permission to all pipelines
5. Save

### Step 2: Create Variable Groups

#### Backend-Secrets

1. Pipelines → Library → Variable Groups → + Variable group
2. Name: `Backend-Secrets`
3. Add variables:

| Variable | Value | Secret? |
|----------|-------|---------|
| `SQL_CONNECTION_STRING` | `postgresql://...` | ✅ Yes |
| `APPINSIGHTS_INSTRUMENTATIONKEY` | (from App Insights) | ✅ Yes |
| `APP_ENV` | `staging` or `production` | No |
| `CORS_ORIGINS` | `https://frontend-staging.azurewebsites.net,https://frontend-prod.azurewebsites.net` | No |

#### Frontend-Config

1. Create new variable group: `Frontend-Config`
2. Add variables:

| Variable | Value | Secret? |
|----------|-------|---------|
| `VITE_API_BASE_STAGING` | `https://backend-staging.azurewebsites.net/api/v1` | No |
| `VITE_API_BASE_PRODUCTION` | `https://backend-prod.azurewebsites.net/api/v1` | No |

### Step 3: Create Environments

1. Pipelines → Environments → New Environment
2. Create:
   - **staging**: No approval required
   - **production**: Require manual approval (add approvers)

---

## CI/CD Pipeline Setup

### Backend Pipeline

1. **Create Pipeline**:
   - Pipelines → Pipelines → New Pipeline
   - Select repository
   - Existing Azure Pipelines YAML file
   - Path: `/azure-pipelines-backend.yml`
   - Continue → Run

2. **Update Variables** in `azure-pipelines-backend.yml`:
   ```yaml
   variables:
     backendAppServiceStaging: 'shopsmart-backend-staging'
     backendAppServiceProduction: 'shopsmart-backend-production'
     azureSubscription: 'Shop-Smart-Service'
     acrName: 'shopsmartacr'
     acrLoginServer: 'shopsmartacr.azurecr.io'
     backendImageRepository: 'shopsmart-backend'
   ```

3. **Link Variable Group**:
   - Edit pipeline → Variables → Variable groups
   - Link `Backend-Secrets`

4. **Pipeline Stages**:
   - ✅ Build: Install dependencies, package app
   - ✅ Lint: Run Flake8 and Black
   - ✅ Test: Run pytest with coverage
   - ✅ Deploy Staging (Container): Build & push image to ACR, deploy container
   - ✅ Deploy Production (Container): Manual approval, deploy container from ACR

### Frontend Pipeline

1. **Create Pipeline**:
   - New Pipeline → Existing YAML file
   - Path: `/azure-pipelines-frontend.yml`

2. **Update Variables**:
   ```yaml
   variables:
     frontendAppServiceStaging: 'shopsmart-frontend-staging'
     frontendAppServiceProduction: 'shopsmart-frontend-production'
     azureSubscription: 'Shop-Smart-Service'
     acrName: 'shopsmartacr'
     acrLoginServer: 'shopsmartacr.azurecr.io'
     frontendImageRepository: 'shopsmart-frontend'
   ```

3. **Link Variable Group**:
   - Link `Frontend-Config`

4. **Pipeline Stages**:
   - ✅ Build: Install dependencies, build React app
   - ✅ Lint: Run ESLint
   - ✅ Deploy Staging (Container): Build & push image to ACR, deploy container
   - ✅ Deploy Production (Container): Manual approval, deploy container from ACR

---

## Containerization & ACR

### Azure Container Registry (ACR)

1. Create ACR (if not already created):

```bash
az acr create \
  --resource-group shopsmart-rg \
  --name shopsmartacr \
  --sku Basic
```

2. Note:
   - **ACR Name**: `shopsmartacr`
   - **Login Server**: `shopsmartacr.azurecr.io`

Update these in both pipeline files if your names differ.

### Backend Docker Image

- Dockerfile: `api/Dockerfile`
- Built and pushed by `azure-pipelines-backend.yml` using:
  - Image: `shopsmartacr.azurecr.io/shopsmart-backend:<build-id>`
- App Services (`shopsmart-backend-staging`, `shopsmart-backend-production`) are configured to run this container.

### Frontend Docker Image

- Dockerfile: `frontend/Dockerfile`
- Built and pushed by `azure-pipelines-frontend.yml` using:
  - Staging image: `shopsmartacr.azurecr.io/shopsmart-frontend:<build-id>`
  - Production image: `shopsmartacr.azurecr.io/shopsmart-frontend:<build-id>-prod`
- App Services (`shopsmart-frontend-staging`, `shopsmart-frontend-production`) are configured to run these containers.

### Converting Existing App Services to Container Mode

The pipelines now deploy using `webAppContainer` type, so you only need:

```bash
az webapp config container set \
  --resource-group shopsmart-rg \
  --name shopsmart-backend-staging \
  --docker-custom-image-name shopsmartacr.azurecr.io/shopsmart-backend:<some-tag> \
  --docker-registry-server-url https://shopsmartacr.azurecr.io

az webapp config container set \
  --resource-group shopsmart-rg \
  --name shopsmart-frontend-staging \
  --docker-custom-image-name shopsmartacr.azurecr.io/shopsmart-frontend:<some-tag> \
  --docker-registry-server-url https://shopsmartacr.azurecr.io
```

After the first successful pipeline run, the YAML will deploy the correct tags automatically.

---

## CORS Configuration

### Backend CORS Setup

The backend reads CORS origins from the `CORS_ORIGINS` environment variable (comma-separated).

**Via Azure Portal**:
1. Azure Portal → App Service → Configuration
2. Add Application Setting:
   - **Name**: `CORS_ORIGINS`
   - **Value**: `https://shopsmart-frontend-staging.azurewebsites.net,https://shopsmart-frontend-production.azurewebsites.net`
3. Save

**Via Azure CLI**:
```bash
az webapp config appsettings set \
  --resource-group shopsmart-rg \
  --name shopsmart-backend-staging \
  --settings CORS_ORIGINS="https://shopsmart-frontend-staging.azurewebsites.net"
```

### Frontend API Configuration

The frontend reads the API base URL from `VITE_API_BASE` during build (configured in pipeline).

---

## Environment Variables

### Backend (Set in App Service Configuration)

| Setting | Staging | Production |
|---------|---------|------------|
| `SQL_CONNECTION_STRING` | Azure SQL connection string | Azure SQL connection string |
| `APP_ENV` | `staging` | `production` |
| `APPINSIGHTS_INSTRUMENTATIONKEY` | (from App Insights) | (from App Insights) |
| `CORS_ORIGINS` | Frontend staging URL | Frontend production URL |

### Frontend (Set in Pipeline Build)

| Variable | Staging | Production |
|---------|---------|------------|
| `VITE_API_BASE` | `https://backend-staging.azurewebsites.net/api/v1` | `https://backend-prod.azurewebsites.net/api/v1` |

---

## Deployment Verification

### Backend Smoke Tests

```bash
export BACKEND_URL=https://shopsmart-backend-staging.azurewebsites.net
./scripts/smoke-test.sh
```

**Manual Checks**:
```bash
# Health check
curl https://shopsmart-backend-staging.azurewebsites.net/health

# Supermarkets
curl https://shopsmart-backend-staging.azurewebsites.net/api/v1/supermarkets/

# API Docs
open https://shopsmart-backend-staging.azurewebsites.net/docs
```

### Frontend Validation

```bash
export FRONTEND_URL=https://shopsmart-frontend-staging.azurewebsites.net
./scripts/validate-frontend.sh
```

**Manual Checks**:
1. Open frontend URL in browser
2. Check browser console (no errors)
3. Verify API calls work (Network tab)
4. Check for mixed content warnings

### End-to-End Test

1. Open frontend: `https://shopsmart-frontend-staging.azurewebsites.net`
2. Add items to shopping list
3. Select supermarkets
4. Click "Compare Prices"
5. Verify results display correctly

---

## Troubleshooting

### Pipeline Failures

**Build Fails**:
- Check Python/Node version matches
- Verify `requirements.txt` or `package.json` is correct
- Check build logs for specific errors

**Deployment Fails**:
- Verify service connection has correct permissions
- Check App Service name matches pipeline variable
- Verify runtime stack is correct (Python 3.11, Node 18)

**Smoke Test Fails**:
- Wait 30-60 seconds after deployment (app startup time)
- Check App Service logs: Azure Portal → App Service → Log stream
- Verify health endpoint: `/health`

### CORS Issues

**Frontend can't call API**:
1. Check `CORS_ORIGINS` includes frontend URL exactly
2. Verify frontend URL uses HTTPS
3. Check browser console for CORS errors
4. Restart App Service after CORS change

**Solution**:
```bash
az webapp config appsettings set \
  --resource-group shopsmart-rg \
  --name shopsmart-backend-staging \
  --settings CORS_ORIGINS="https://shopsmart-frontend-staging.azurewebsites.net"
```

### Database Connection Issues

**Connection String Format**:
```
postgresql://username:password@server.database.azure.com:5432/database?sslmode=require
```

**Verify Connection**:
- Check App Service logs
- Verify SQL Server firewall allows Azure services
- Test connection string locally

---

## Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure DevOps Pipelines                     │
├─────────────────────────────────────────────────────────────┤
│  Backend CI/CD          │  Frontend CI/CD                    │
│  - Build                │  - Build                           │
│  - Lint                 │  - Lint                            │
│  - Test                 │  - Deploy                          │
│  - Deploy Staging       │  - Deploy Staging                  │
│  - Deploy Production    │  - Deploy Production               │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Azure Resources                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  App Service      │         │  App Service      │        │
│  │  (Backend)        │────────▶│  (Frontend)       │        │
│  │  - Staging        │  API    │  - Staging        │        │
│  │  - Production     │  Calls  │  - Production     │        │
│  └──────────────────┘         └──────────────────┘        │
│         │                                 │                  │
│         │                                 │                  │
│         ▼                                 │                  │
│  ┌──────────────────┐                    │                  │
│  │  Azure SQL       │                    │                  │
│  │  Database        │                    │                  │
│  └──────────────────┘                    │                  │
│                                           │                  │
│  ┌──────────────────┐                    │                  │
│  │  Application     │◀───────────────────┘                  │
│  │  Insights        │   Telemetry                           │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

### Environment Flow

```
Development → Staging → Production
     │           │           │
     │           │           │
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Local  │ │  Azure  │ │  Azure  │
│  Dev    │ │ Staging │ │   Prod  │
└─────────┘ └─────────┘ └─────────┘
     │           │           │
     │           │    Manual │
     │           │   Approval│
     │           │           │
     └───────────┴───────────┘
              │
              ▼
         Production
```

---

## Next Steps

1. ✅ Set up Azure resources
2. ✅ Configure Azure DevOps pipelines
3. ✅ Create variable groups
4. ✅ Deploy to staging
5. ✅ Run smoke tests
6. ✅ Configure CORS
7. ✅ Test end-to-end
8. ✅ Deploy to production (with approval)

---

## Support

For issues:
- Check pipeline logs in Azure DevOps
- Review App Service logs in Azure Portal
- Check Application Insights for errors
- Review this documentation
