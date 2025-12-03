"""
FastAPI main application file
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from app.config import settings
from app.db import engine, Base
from app.middleware import LoggingMiddleware
from app.routes import health, products, supermarkets, prices, compare, catalog, shopping_lists
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database migrations are managed via Alembic
# Run migrations with: alembic upgrade head
# In production, migrations are the source of truth (no manual table creation)
# Skip table creation in test environment
if settings.app_env != "test":
    # Note: In production, use Alembic migrations instead of create_all
    # This is kept for backward compatibility in development
    # For production deployments, ensure migrations are run via CI/CD or startup script
    try:
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        logger.warning(f"Could not run Alembic migrations: {e}. Falling back to create_all.")
        Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
# OpenAPI is automatically enabled by FastAPI (available at /docs, /redoc, /openapi.json)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Add logging middleware for structured request/response logging
app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    FastAPICORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers for structured error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors (422)"""
    errors = exc.errors()
    error_messages = [f"{error['loc']}: {error['msg']}" for error in errors]
    message = "; ".join(error_messages) if error_messages else "Validation error"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "UnprocessableEntity", "message": message},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured error responses"""
    error_type = _get_error_type(exc.status_code)

    return JSONResponse(
        status_code=exc.status_code, content={"error": error_type, "message": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions (500)"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    error_detail = "Internal server error" if not settings.debug else str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "message": error_detail},
    )


def _get_error_type(status_code: int) -> str:
    """Map status code to error type"""
    error_types = {
        400: "BadRequest",
        401: "Unauthorized",
        403: "Forbidden",
        404: "NotFound",
        422: "UnprocessableEntity",
        500: "InternalServerError",
        502: "BadGateway",
        503: "ServiceUnavailable",
    }
    return error_types.get(status_code, "Error")


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(
    supermarkets.router, prefix=f"{settings.api_prefix}/supermarkets", tags=["Supermarkets"]
)
app.include_router(products.router, prefix=f"{settings.api_prefix}/products", tags=["Products"])
app.include_router(prices.router, prefix=f"{settings.api_prefix}/prices", tags=["Prices"])
app.include_router(compare.router, prefix=f"{settings.api_prefix}/compare", tags=["Compare"])
app.include_router(catalog.router, prefix=f"{settings.api_prefix}", tags=["Catalog"])
app.include_router(shopping_lists.router, prefix=f"{settings.api_prefix}", tags=["Shopping Lists"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Product Comparison API",
        "version": settings.app_version,
        "docs": "/docs",
    }
