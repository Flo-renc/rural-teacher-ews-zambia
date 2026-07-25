"""
Database connection configuration.

This module configures the SQLAlchemy engine and session factory
for the SQLite database used by the Teacher Attrition Early
Warning System prototype.

SQLite was selected for this prototype because it is lightweight,
self-contained, and simplifies deployment. The configuration can
be replaced with PostgreSQL or MySQL in future production
implementations without affecting the application's data models.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


logger = logging.getLogger(__name__)

# Database Configuration

# SQLite database file stored in project root
DATABASE_URL = "sqlite:///./teacher_ews.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base Model

class Base(DeclarativeBase):
    pass

# Database Dependencies

def get_db():

    """
    Provide a database session for FastAPI dependencies.

    Yields:
        Session: Active SQLAlchemy database session.

    The session is automatically closed after the request
    has completed.
    """    
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def create_tables():

    """
    Create all database tables defined by the ORM models.

    This function is typically called during application
    startup to ensure that all required tables exist.
    """

    # Import models so SQLAlchemy knows the tables
    from app.models import db_models  # noqa

    Base.metadata.create_all(
        bind=engine
    )

    logger.info("SQLite tables created.")