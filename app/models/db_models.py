"""
SQLAlchemy ORM models — mirrors the MySQL schema exactly.
Importing this module registers all models with Base.metadata.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime,
    Enum as SAEnum, ForeignKey, SmallInteger, Index,
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


class School(Base):
    __tablename__ = "schools"

    school_code = Column(String(20),  primary_key=True, nullable=False)
    name        = Column(String(200), nullable=False)
    district    = Column(String(100), nullable=False)
    province    = Column(String(100), nullable=False)
    school_type = Column(String(50))
    is_rural    = Column(SmallInteger, default=1)
    created_at  = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teacher_records = relationship("TeacherRecord",  back_populates="school", cascade="all, delete")
    predictions     = relationship("RiskPrediction", back_populates="school", cascade="all, delete")

    __table_args__ = (
        Index("idx_district", "district"),
        Index("idx_province", "province"),
    )


class TeacherRecord(Base):
    __tablename__ = "teacher_records"

    record_id       = Column(Integer,     primary_key=True, autoincrement=True)
    school_code     = Column(String(20),  ForeignKey("schools.school_code", ondelete="CASCADE"), nullable=False)
    year            = Column(Integer,     nullable=False)
    teacher_count   = Column(Integer)
    qualified_count = Column(Integer)
    ptr             = Column(Float)          # pupil-teacher ratio
    enrolment       = Column(Integer)
    attrition_est   = Column(Integer)
    created_at      = Column(DateTime, default=datetime.utcnow)

    school = relationship("School", back_populates="teacher_records")

    __table_args__ = (
        Index("idx_school_year", "school_code", "year"),
    )


class MLModel(Base):
    __tablename__ = "ml_models"

    model_version = Column(String(50),  primary_key=True, nullable=False)
    algorithm     = Column(String(100), nullable=False)
    f1_score      = Column(Float)
    recall_score  = Column(Float)
    auc_score     = Column(Float)
    trained_at    = Column(DateTime, default=datetime.utcnow)
    artefact_path = Column(String(500))
    is_active     = Column(SmallInteger, default=0)
    notes         = Column(Text)

    predictions = relationship("RiskPrediction", back_populates="model", cascade="all, delete")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    prediction_id  = Column(Integer,    primary_key=True, autoincrement=True)
    school_code    = Column(String(20), ForeignKey("schools.school_code",    ondelete="CASCADE"), nullable=False)
    model_version  = Column(String(50), ForeignKey("ml_models.model_version", ondelete="CASCADE"), nullable=False)
    risk_score     = Column(Float,      nullable=False)
    risk_label     = Column(SAEnum("high_risk", "not_at_risk"), nullable=False)
    shap_json      = Column(Text)
    confidence_pct = Column(Float)
    predicted_at   = Column(DateTime, default=datetime.utcnow)

    school = relationship("School",  back_populates="predictions")
    model  = relationship("MLModel", back_populates="predictions")

    __table_args__ = (
        Index("idx_school_predicted", "school_code", "predicted_at"),
    )


class User(Base):
    __tablename__ = "users"

    user_id       = Column(Integer,     primary_key=True, autoincrement=True)
    username      = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(
        SAEnum("district_officer", "data_admin", "viewer"),
        default="viewer",
    )
    province   = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_username", "username"),
    )
