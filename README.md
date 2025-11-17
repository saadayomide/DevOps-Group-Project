ShopSmart — TeamC (Sprint 1)

Quick start (local):
1. Copy .env.example -> .env and set APPINSIGHTS_INSTRUMENTATIONKEY
2. Install deps: python -m pip install -r requirements.txt
3. Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000

CI/CD:
- azure_pipelines.yml is configured to Build → Lint → Test → Publish → Deploy (staging)
- setup-azure.sh will create Resource Group, App Service plan, Web App, Application Insights and Key Vault, and will wire Key Vault secret to the Web App.

Monitoring:
- App Insights needs an instrumentation key (or set via Key Vault). Telemetry is initialized at startup when APPINSIGHTS_INSTRUMENTATIONKEY is present.

See docs/deployment_guide.md for more details.