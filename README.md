# ShopSmart — Price Comparison Application

A full-stack application for comparing product prices across multiple supermarkets, built with FastAPI (backend) and React (frontend), deployed to Azure with CI/CD via GitHub Actions.

## Quick Start

### Backend (Local Development)
1. Navigate to the `api/` directory
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (see `api/.env.example`)
5. Run the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend (Local Development)
1. Navigate to the `frontend/` directory
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## CI/CD

- **GitHub Actions** workflows in `.github/workflows/` handle automated builds, tests, and deployments
- **Backend**: Builds Docker image, runs tests, pushes to Azure Container Registry (ACR), and deploys to Azure App Service
- **Frontend**: Builds Docker image, pushes to ACR, and deploys to Azure App Service
- **Environments**: Staging (on `teamC2` branch) and Production (on `main` branch)

## Project Structure

```
├── api/                    # Backend FastAPI application
│   ├── app/                # Application code
│   ├── tests/              # Test suite
│   ├── alembic/            # Database migrations
│   └── Dockerfile          # Container image definition
├── frontend/               # Frontend React application
│   ├── src/                # Source code
│   └── Dockerfile          # Container image definition
├── docs/                   # Documentation
└── .github/workflows/      # CI/CD pipelines
```

## Documentation

- **DevOps Guide**: `docs/DEVOPS_GUIDE.md` - Complete deployment and infrastructure setup
- **Architecture**: `api/docs/ARCHITECTURE.md` - Backend architecture details
- **Testing**: `api/docs/TESTING.md` - Testing guidelines

## Monitoring

- Application Insights is configured for production deployments
- Connection string is set via environment variables in Azure App Service
