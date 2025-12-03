"""
Application configuration settings
Reads SQL_CONNECTION_STRING and APP_ENV from environment variables
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,  # Allows case-insensitive env var matching
        env_file_encoding="utf-8",
        # Explicitly map environment variable names
        env_prefix="",
    )

    # Application
    app_name: str = "FastAPI Product Comparison API"
    app_version: str = "0.1.0"
    # APP_ENV: development, staging, production
    # With case_sensitive=False, both APP_ENV and app_env work
    app_env: str = "development"

    # Database - read from SQL_CONNECTION_STRING environment variable
    # With case_sensitive=False, both SQL_CONNECTION_STRING and sql_connection_string work
    sql_connection_string: str = "postgresql://postgres:postgres@localhost:5432/product_db"

    # API
    api_prefix: str = "/api/v1"
    # CORS origins - read from CORS_ORIGINS env var (comma-separated string)
    # Don't parse as List[str] to avoid JSON parsing issues
    # Use allowed_cors_origins property instead

    @property
    def allowed_cors_origins(self) -> List[str]:
        """Get CORS origins from environment variable or default"""
        import os

        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            # Split comma-separated values and strip whitespace
            return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
        # Default: allow all origins in development
        return ["*"]

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def debug(self) -> bool:
        """Debug mode based on APP_ENV"""
        return self.app_env == "development"


settings = Settings()
