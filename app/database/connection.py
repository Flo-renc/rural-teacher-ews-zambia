"""
Database connection — MySQL via SQLAlchemy (synchronous).
Uses environment variables for credentials; falls back to SQLite for local dev.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)

DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "3306")
DB_NAME     = os.getenv("DB_NAME",     "teacher_ews")
DB_USER     = os.getenv("DB_USER",     "ews_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

if DB_PASSWORD:
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
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
    """FastAPI dependency — yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all ORM-defined tables in the database."""
    from app.models import db_models  # noqa: F401 — registers models with Base
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created (or already exist).")
