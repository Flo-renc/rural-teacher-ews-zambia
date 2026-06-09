"""
Database connection — MySQL via SQLAlchemy (synchronous).
Uses environment variables for credentials; falls back to SQLite for local dev.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import logging

logger = logging.getLogger(__name__)

# Build connection string from env vars
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_NAME     = os.getenv("DB_NAME", "teacher_ews")
DB_USER     = os.getenv("DB_USER", "ews_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Use SQLite for local dev if no MySQL credentials are set
if DB_PASSWORD:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = "sqlite:///./teacher_ews.db"
    logger.warning("No DB_PASSWORD set — using SQLite for local development.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in ORM models."""
    from app.models import db_models  # noqa: F401 — registers models with Base
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created (or already exist).")