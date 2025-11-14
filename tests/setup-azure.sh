#!/bin/bash

# ShopSmart Azure Infrastructure Setup Script
# This script sets up all required Azure resources for the ShopSmart application

set -e  # Exit on any error

# Configuration Variables
RESOURCE_GROUP="shopsmart-rg"
LOCATION="westeurope"
APP_SERVICE_PLAN="shopsmart-plan"
WEB_APP_NAME="shopsmart-backend-staging"  # Change this to your unique name
APP_INSIGHTS_NAME="shopsmart-insights"
KEY_VAULT_NAME="shopsmart-kv-$(openssl rand -hex 4)"  # Unique name
SKU="B1"  # Basic tier

echo "================================================"
echo "ShopSmart Azure Infrastructure Setup"
echo "================================================"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Error: Azure CLI is not installed"
    echo "Please install it from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

echo "✅ Azure CLI found"

# Login to Azure (if not already logged in)
echo ""
echo "Checking Azure login status..."
az account show &> /dev/null || az login

SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "✅ Logged in to subscription: $SUBSCRIPTION_NAME"

echo ""
echo "================================================"
echo "Configuration:"
echo "================================================"
echo "Resource Group:     $RESOURCE_GROUP"
echo "Location:           $LOCATION"
echo "App Service Plan:   $APP_SERVICE_PLAN"
echo "Web App:            $WEB_APP_NAME"
echo "App Insights:       $APP_INSIGHTS_NAME"
echo "Key Vault:          $KEY_VAULT_NAME"
echo "================================================"
echo ""

read -p "Continue with this configuration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 0
fi

# Step 1: Create Resource Group
echo ""
echo "📦 Step 1/6: Creating Resource Group..."
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "⚠️  Resource group already exists, skipping..."
else
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION
    echo "✅ Resource group created"
fi

# Step 2: Create App Service Plan
echo ""
echo "📦 Step 2/6: Creating App Service Plan..."
if az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "⚠️  App Service Plan already exists, skipping..."
else
    az appservice plan create \
        --name $APP_SERVICE_PLAN \
        --resource-group $RESOURCE_GROUP \
        --sku $SKU \
        --is-linux
    echo "✅ App Service Plan created"
fi

# Step 3: Create Web App
echo ""
echo "🌐 Step 3/6: Creating Web App..."
if az webapp show --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "⚠️  Web App already exists, skipping..."
else
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_SERVICE_PLAN \
        --name $WEB_APP_NAME \
        --runtime "PYTHON:3.11"
    echo "✅ Web App created"
fi

# Step 4: Create Application Insights
echo ""
echo "📊 Step 4/6: Creating Application Insights..."
if az monitor app-insights component show --app $APP_INSIGHTS_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "⚠️  Application Insights already exists, getting key..."
else
    az monitor app-insights component create \
        --app $APP_INSIGHTS_NAME \
        --location $LOCATION \
        --resource-group $RESOURCE_GROUP \
        --application-type web
    echo "✅ Application Insights created"
fi

INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app $APP_INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey -o tsv)

echo "✅ Instrumentation Key retrieved"

# Step 5: Create Key Vault
echo ""
echo "🔐 Step 5/6: Creating Key Vault..."
if az keyvault show --name $KEY_VAULT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "⚠️  Key Vault already exists, skipping..."
else
    az keyvault create \
        --name $KEY_VAULT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
    echo "✅ Key Vault created"
fi

# Store Application Insights key in Key Vault
echo "Storing secrets in Key Vault..."
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "AppInsightsInstrumentationKey" \
    --value "$INSTRUMENTATION_KEY" \
    --output none

echo "✅ Secrets stored in Key Vault"

# Step 6: Configure Web App
echo ""
echo "⚙️  Step 6/6: Configuring Web App..."

# Enable managed identity for the Web App
echo "Enabling managed identity..."
az webapp identity assign \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output none

PRINCIPAL_ID=$(az webapp identity show \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query principalId -o tsv)

echo "✅ Managed identity enabled"

# Grant Web App access to Key Vault
echo "Granting Key Vault access..."
az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $PRINCIPAL_ID \
    --secret-permissions get list \
    --output none

echo "✅ Key Vault access granted"

# Configure App Settings
echo "Configuring application settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY" \
        ENVIRONMENT="staging" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    --output none

echo "✅ App settings configured"

# Configure startup command
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port 8000" \
    --output none

echo "✅ Startup command configured"

# Enable CORS (if needed)
az webapp cors add \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --allowed-origins "*" \
    --output none

echo "✅ CORS configured"

# Summary
echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "📋 Resource Summary:"
echo "-------------------"
echo "Resource Group:     $RESOURCE_GROUP"
echo "Location:           $LOCATION"
echo ""
echo "🌐 Web Application:"
echo "   Name:            $WEB_APP_NAME"
echo "   URL:             https://$WEB_APP_NAME.azurewebsites.net"
echo "   Runtime:         Python 3.11"
echo ""
echo "📊 Application Insights:"
echo "   Name:            $APP_INSIGHTS_NAME"
echo "   Instrumentation: $INSTRUMENTATION_KEY"
echo ""
echo "🔐 Key Vault:"
echo "   Name:            $KEY_VAULT_NAME"
echo ""
echo "================================================"
echo ""
echo "📝 Next Steps:"
echo "-------------------"
echo "1. Configure Azure DevOps pipeline"
echo "   - Update azureSubscription in azure-pipelines.yml"
echo "   - Update appServiceName to '$WEB_APP_NAME'"
echo ""
echo "2. Create Service Connection in Azure DevOps:"
echo "   - Go to Project Settings → Service Connections"
echo "   - Create new Azure Resource Manager connection"
echo "   - Name it: 'BCSAI2025-DEVOPS-STUDENTS-A'"
echo "   - Select subscription and resource group"
echo ""
echo "3. Push code to repository to trigger pipeline"
echo ""
echo "4. Access Application:"
echo "   - API: https://$WEB_APP_NAME.azurewebsites.net"
echo "   - Docs: https://$WEB_APP_NAME.azurewebsites.net/docs"
echo "   - Health: https://$WEB_APP_NAME.azurewebsites.net/health"
echo ""
echo "5. Monitor Application:"
echo "   - Portal: https://portal.azure.com"
echo "   - Navigate to: $RESOURCE_GROUP → $APP_INSIGHTS_NAME"
echo ""
echo "================================================"

# Save configuration to file
CONFIG_FILE="azure-config.txt"
cat > $CONFIG_FILE << EOF
ShopSmart Azure Configuration
Generated: $(date)

Resource Group: $RESOURCE_GROUP
Location: $LOCATION
App Service Plan: $APP_SERVICE_PLAN
Web App: $WEB_APP_NAME
Web App URL: https://$WEB_APP_NAME.azurewebsites.net
Application Insights: $APP_INSIGHTS_NAME
Instrumentation Key: $INSTRUMENTATION_KEY
Key Vault: $KEY_VAULT_NAME

Update these values in your configuration files:
- azure-pipelines.yml: appServiceName = '$WEB_APP_NAME'
- Azure DevOps: Create service connection to this subscription
EOF

echo "✅ Configuration saved to: $CONFIG_FILE"
echo ""