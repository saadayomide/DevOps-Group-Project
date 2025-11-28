"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create engine with connection pooling (pool_size=5)
# SQL_CONNECTION_STRING is read from environment variable
# SQLite doesn't support pool_size and max_overflow, so conditionally apply them
engine_kwargs = {"pool_pre_ping": True, "echo": settings.debug}  # Verify connections before using

# Only use connection pooling for non-SQLite databases
if not settings.sql_connection_string.startswith("sqlite"):
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
else:
    # SQLite requires check_same_thread=False for async/threading compatibility
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.sql_connection_string, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI routes
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
