"""
Database connection — SQLite via SQLAlchemy.

Prototype database for the Teacher Attrition Early Warning System.
Production migration to PostgreSQL/MySQL can be done later.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


logger = logging.getLogger(__name__)


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


class Base(DeclarativeBase):
    pass


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def create_tables():

    # Import models so SQLAlchemy knows the tables
    from app.models import db_models  # noqa

    Base.metadata.create_all(
        bind=engine
    )

    logger.info("SQLite tables created.")