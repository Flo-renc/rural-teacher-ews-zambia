"""
ORM models — mirrors the MySQL ERD from the proposal (Chapter 3.7.3).
Tables: schools, teacher_records, risk_predictions, ml_models, users
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database.connection import Base


class RiskLabel(str, enum.Enum):
    HIGH_RISK = "high_risk"
    NOT_AT_RISK = "not_at_risk"


class UserRole(str, enum.Enum):
    DISTRICT_OFFICER = "district_officer"
    DATA_ADMIN = "data_admin"
    VIEWER = "viewer"


class School(Base):
    __tablename__ = "schools"

    school_code   = Column(String(20), primary_key=True, index=True)
    name          = Column(String(200), nullable=False)
    district      = Column(String(100), nullable=False, index=True)
    province      = Column(String(100), nullable=False, index=True)
    school_type   = Column(String(50))          # GRZ, Community, Private, Grant-Aided
    is_rural      = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    teacher_records   = relationship("TeacherRecord",   back_populates="school")
    risk_predictions  = relationship("RiskPrediction",  back_populates="school")


class TeacherRecord(Base):
    __tablename__ = "teacher_records"

    record_id       = Column(Integer, primary_key=True, autoincrement=True)
    school_code     = Column(String(20), ForeignKey("schools.school_code"), nullable=False, index=True)
    year            = Column(Integer, nullable=False)
    teacher_count   = Column(Integer)
    qualified_count = Column(Integer)
    ptr             = Column(Float)
    enrolment       = Column(Integer)
    attrition_est   = Column(Integer, nullable=True)
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school = relationship("School", back_populates="teacher_records")


class MLModel(Base):
    __tablename__ = "ml_models"

    model_version  = Column(String(50), primary_key=True)
    algorithm      = Column(String(100), nullable=False)
    f1_score       = Column(Float)
    recall_score   = Column(Float)
    auc_score      = Column(Float)
    trained_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    artefact_path  = Column(String(500))
    is_active      = Column(Boolean, default=False)
    notes          = Column(Text, nullable=True)

    predictions = relationship("RiskPrediction", back_populates="model")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    prediction_id  = Column(Integer, primary_key=True, autoincrement=True)
    school_code    = Column(String(20), ForeignKey("schools.school_code"), nullable=False, index=True)
    model_version  = Column(String(50), ForeignKey("ml_models.model_version"), nullable=False)
    risk_score     = Column(Float, nullable=False)       # probability 0–1
    risk_label     = Column(Enum(RiskLabel), nullable=False)
    shap_json      = Column(Text, nullable=True)         # JSON-serialised SHAP values
    confidence_pct = Column(Float, nullable=True)
    predicted_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school = relationship("School", back_populates="risk_predictions")
    model  = relationship("MLModel", back_populates="predictions")


class User(Base):
    __tablename__ = "users"

    user_id       = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(Enum(UserRole), default=UserRole.VIEWER)
    province      = Column(String(100), nullable=True)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
