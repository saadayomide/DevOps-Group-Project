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

See docs/deployment_guide.md for more details.s

## TeamB2 branch (what was added)
This branch adds a minimal /api router and basic integration endpoints used by tests:
- New file: api.py — exposes /api/supermarkets, /api/products, /api/prices, /api/compare
- Tests: basic smoke tests under tests/ (and any integration tests already present)

Quick local steps
1. Switch to branch:
   git fetch origin
   git switch teamB2 || git switch -c teamB2 --track origin/teamB2

2. Create & activate venv (macOS):
   python3 -m venv .venv
   source .venv/bin/activate

3. Install deps:
   python -m pip install --upgrade pip
   pip install -r requirements.txt

4. Run app:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

5. Run tests:
   python -m pytest -q
   # or run just the smoke tests:
   python -m pytest tests/test_api_basic.py -q

Notes
- Ensure APPINSIGHTS_INSTRUMENTATIONKEY is set in .env if you want telemetry initialized.
- If you need a tiny extra commit, update README or .gitignore and commit/push as shown below.