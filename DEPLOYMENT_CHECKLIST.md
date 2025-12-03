# Deployment Checklist

## ✅ Completed
- [x] Repository cleaned up (legacy files removed)
- [x] GitHub Actions workflows created (`.github/workflows/backend.yml` and `frontend.yml`)
- [x] Dockerfiles created for both backend and frontend
- [x] CORS configuration fixed in backend
- [x] Documentation updated

## 🔲 Remaining Steps

### 1. GitHub Secrets Configuration

Go to: **GitHub Repo → Settings → Secrets and variables → Actions**

Add the following secrets:

#### Required Secrets:
- [ ] `AZURE_CREDENTIALS` - Service principal JSON (see below)
- [ ] `AZURE_ACR_USERNAME` - ACR admin username (usually the ACR name: `shopsmartacr`)
- [ ] `AZURE_ACR_PASSWORD` - ACR admin password
- [ ] `AZURE_BACKEND_STAGING_APP_NAME` - Your staging backend app name
- [ ] `AZURE_BACKEND_PRODUCTION_APP_NAME` - Your production backend app name
- [ ] `AZURE_FRONTEND_STAGING_APP_NAME` - Your staging frontend app name
- [ ] `AZURE_FRONTEND_PRODUCTION_APP_NAME` - Your production frontend app name

#### How to get AZURE_CREDENTIALS:
```bash
az ad sp create-for-rbac \
  --name shopsmart-github-actions \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/BCSAI2025-DEVOPS-STUDENT-5A \
  --sdk-auth
```

Copy the entire JSON output and paste it as the value for `AZURE_CREDENTIALS`.

#### How to get ACR credentials:
```bash
# Enable admin user
az acr update --name shopsmartacr --admin-enabled true

# Get credentials
az acr credential show --name shopsmartacr
```

### 2. GitHub Environments

Go to: **GitHub Repo → Settings → Environments**

Create two environments:
- [ ] `staging` - No approval required
- [ ] `production` - Optional: Add required reviewers for manual approval

### 3. Azure App Service Configuration

#### Backend App Services

For both staging and production backend App Services, configure:

**Via Azure Portal:**
1. Go to App Service → Configuration → Application settings
2. Add/Update:
   - [ ] `SQL_CONNECTION_STRING` - Your PostgreSQL connection string
   - [ ] `APP_ENV` - `staging` or `production`
   - [ ] `CORS_ORIGINS` - Comma-separated frontend URLs:
     - Staging: `https://<frontend-staging-name>.azurewebsites.net`
     - Production: `https://<frontend-production-name>.azurewebsites.net`
   - [ ] `APPINSIGHTS_CONNECTION_STRING` - (Optional) Application Insights connection string

**Via Azure CLI:**
```bash
# Staging Backend
az webapp config appsettings set \
  --resource-group BCSAI2025-DEVOPS-STUDENT-5A \
  --name <your-backend-staging-app-name> \
  --settings \
    SQL_CONNECTION_STRING="<postgres-connection-string>" \
    APP_ENV="staging" \
    CORS_ORIGINS="https://<frontend-staging-name>.azurewebsites.net"

# Production Backend
az webapp config appsettings set \
  --resource-group BCSAI2025-DEVOPS-STUDENT-5A \
  --name <your-backend-production-app-name> \
  --settings \
    SQL_CONNECTION_STRING="<postgres-connection-string>" \
    APP_ENV="production" \
    CORS_ORIGINS="https://<frontend-production-name>.azurewebsites.net"
```

#### Frontend App Services

Frontend App Services don't need environment variables (API URL is baked into the Docker image during build).

### 4. Configure App Services for Containers

Ensure both backend and frontend App Services are configured to use containers:

**Via Azure Portal:**
1. Go to App Service → Deployment Center
2. Select "Container Registry" as source
3. Choose "Azure Container Registry"
4. Select your ACR: `shopsmartacr`
5. Select image: `shopsmart-backend` or `shopsmart-frontend`
6. Tag: Leave as `latest` (will be updated by GitHub Actions)

**Note:** The GitHub Actions workflow will automatically update the container image on each deployment, so you can leave the initial setup as `latest`.

### 5. Verify ACR Access

Ensure the App Services can pull from ACR:

```bash
# Enable managed identity (optional but recommended)
az webapp identity assign \
  --resource-group BCSAI2025-DEVOPS-STUDENT-5A \
  --name <app-name>

# Grant ACR pull permission
az role assignment create \
  --assignee <principal-id> \
  --scope /subscriptions/<subscription-id>/resourceGroups/BCSAI2025-DEVOPS-STUDENT-5A/providers/Microsoft.ContainerRegistry/registries/shopsmartacr \
  --role AcrPull
```

Or use admin credentials (simpler):
- Ensure ACR admin user is enabled (already done above)
- App Service will use admin credentials automatically

### 6. Trigger Deployment

Once all secrets and configurations are in place:

1. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "Clean up repository and prepare for deployment"
   git push origin teamC2  # For staging
   ```

2. **Monitor GitHub Actions:**
   - Go to **Actions** tab in GitHub
   - Watch the workflow runs
   - Backend workflow should: Build → Test → Push to ACR → Deploy
   - Frontend workflow should: Build → Push to ACR → Deploy

3. **Verify Deployment:**
   ```bash
   # Backend health check
   curl https://<backend-staging-app-name>.azurewebsites.net/health

   # Frontend check
   curl -I https://<frontend-staging-app-name>.azurewebsites.net
   ```

### 7. Production Deployment

After staging is verified:
1. Merge `teamC2` → `main`
2. Push to `main` branch
3. Approve production deployment (if you set up manual approval)
4. Monitor the production deployment

## Troubleshooting

### If deployment fails:
1. Check GitHub Actions logs for errors
2. Verify all secrets are correctly set
3. Check App Service logs: `az webapp log tail --name <app-name> --resource-group BCSAI2025-DEVOPS-STUDENT-5A`
4. Verify ACR access: `az acr repository list --name shopsmartacr`

### Common Issues:
- **401 Unauthorized**: Check ACR credentials
- **Image not found**: Ensure image was pushed to ACR
- **CORS errors**: Verify `CORS_ORIGINS` setting in backend App Service
- **Database connection errors**: Verify `SQL_CONNECTION_STRING` is correct

## Next Steps After Deployment

1. Test the full application flow
2. Monitor Application Insights
3. Set up alerts (optional)
4. Document any custom configurations
