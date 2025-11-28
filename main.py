from fastapi import FastAPI
import os

# router.py is at repo root and defines /teamc routes
from fastapi import FastAPI
import os

# router.py is at repo root and defines /teamc routes
from router import router  # relative import works when running module as package
from telemetry import init_telemetry

# NEW: include the API router that serves /api endpoints
from api import router as api_router

app = FastAPI(title="ShopSmart TeamC Backend", version="0.1.0")
app.include_router(router)
app.include_router(api_router)


@app.get("/", tags=["root"])
async def root():
    return {"service": "ShopSmart TeamC", "status": "ok"}


@app.get("/health", tags=["root"])
async def health():
    return {"status": "healthy"}


@app.on_event("startup")
async def on_startup():
    # Application Insights key should be provided via env var or Key Vault at runtime
    ikey = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")
    init_telemetry(app, ikey)
