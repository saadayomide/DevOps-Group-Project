# Team C - DevOps & Deployment Guide (GitHub Actions)

Complete guide for Azure infrastructure, GitHub Actions CI/CD, and container-based deployment.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Azure Infrastructure Setup](#azure-infrastructure-setup)
3. [GitHub Actions Configuration](#github-actions-configuration)
4. [CI/CD Workflow Overview](#cicd-workflow-overview)
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

# Run Smoke Tests (optional - can be done manually via curl)
export BACKEND_URL=https://shopsmart-backend-staging.azurewebsites.net
curl -f https://shopsmart-backend-staging.azurewebsites.net/health
```

---

## Azure Infrastructure Setup

### Step 1: Create Azure Resources

Create the following resources manually via Azure Portal or Azure CLI:

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

## GitHub Actions Configuration

### 1. Create Environments in GitHub

In your GitHub repository:

1. Go to **Settings → Environments**.
2. Create:
   - Environment **`staging`** (no approval required).
   - Environment **`production`** (add required reviewers for manual approval).

These are used by the workflows in `.github/workflows/backend.yml` and `.github/workflows/frontend.yml`.

### 2. Create Azure Service Principal & Secret

Create a service principal that GitHub Actions will use:

```bash
az ad sp create-for-rbac \
  --name shopsmart-github-actions \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/BCSAI2025-DEVOPS-STUDENT-5A \
  --sdk-auth
```

Copy the **JSON output** and save it as a GitHub repo secret:

- **Name**: `AZURE_CREDENTIALS`
- **Value**: (entire JSON from the command above)

### 3. Add Other GitHub Secrets (Optional)

If your backend code expects extra secrets (e.g. DB password separately), you can also create:

- `SQL_CONNECTION_STRING` (same value as in App Service)
- `APPINSIGHTS_CONNECTION_STRING` or `APPINSIGHTS_INSTRUMENTATIONKEY`

---

## CI/CD Workflow Overview

### Backend Workflow (`.github/workflows/backend.yml`)

Triggered on push to `main` for `api/**`:

- **Job 1 – Build, Test & Push Image**
  - Install Python 3.11
  - Install dependencies from `api/requirements.txt`
  - Run `pytest` for the backend
  - Login to Azure using `AZURE_CREDENTIALS`
  - Login to ACR `shopsmartacr`
  - Build Docker image from `api/Dockerfile` and push to:
    - `shopsmartacr.azurecr.io/shopsmart-backend:<git-sha>`

- **Job 2 – Deploy Staging**
  - Environment: `staging`
  - Configure App Service `shopsmart-backend-staging` to use the pushed image
  - Restart the app

- **Job 3 – Deploy Production**
  - Environment: `production` (manual approval via GitHub environment)
  - Configure App Service `shopsmart-backend-production` to use the same image
  - Restart the app

### Frontend Workflow (`.github/workflows/frontend.yml`)

Triggered on push to `main` for `frontend/**`:

- **Job 1 – Build & Push Images**
  - Login to Azure and ACR
  - Build **staging image** from `frontend/Dockerfile` with:
    - `VITE_API_BASE=https://shopsmart-backend-staging.azurewebsites.net/api/v1`
    - Tag: `shopsmartacr.azurecr.io/shopsmart-frontend:<git-sha>`
  - Build **production image** with:
    - `VITE_API_BASE=https://shopsmart-backend-production.azurewebsites.net/api/v1`
    - Tag: `shopsmartacr.azurecr.io/shopsmart-frontend:<git-sha>-prod`
  - Push both images to ACR

- **Job 2 – Deploy Staging**
  - Environment: `staging`
  - Configure App Service `shopsmart-frontend-staging` to use the staging image
  - Restart the app

- **Job 3 – Deploy Production**
  - Environment: `production`
  - Configure App Service `shopsmart-frontend-production` to use the production image
  - Restart the app

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

Update these in both workflow files if your names differ.

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
# Check frontend loads
curl -I https://shopsmart-frontend-staging.azurewebsites.net

# Verify HTML structure
curl https://shopsmart-frontend-staging.azurewebsites.net | grep -q 'id="root"'
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

### Workflow & Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                           │
├─────────────────────────────────────────────────────────────┤
│  Backend Workflow        │  Frontend Workflow                │
│  - Build & Test          │  - Build (Vite)                   │
│  - Push Image to ACR     │  - Push Images to ACR             │
│  - Deploy Staging        │  - Deploy Staging                 │
│  - Deploy Production     │  - Deploy Production              │
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
