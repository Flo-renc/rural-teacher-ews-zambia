"""
SQLAlchemy ORM models — province-level EWS schema.
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime,
    Enum as SAEnum, ForeignKey, SmallInteger, Index, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


class ProvinceData(Base):
    """Raw bulletin data per province per year."""
    __tablename__ = "province_data"

    id                        = Column(Integer, primary_key=True, autoincrement=True)
    province                  = Column(String(100), nullable=False)
    year                      = Column(Integer,     nullable=False)
    teacher_count_primary     = Column(Integer)
    student_enrolment_primary = Column(Integer)
    ptr_primary_bulletin      = Column(Float)
    primary_schools           = Column(Integer)
    rural_schools             = Column(Integer)
    urban_schools             = Column(Integer)
    created_at                = Column(DateTime, default=datetime.utcnow)

   
    __table_args__ = (
        UniqueConstraint("province", "year", name="uq_province_year"),
        Index("idx_pd_province", "province"),
        Index("idx_pd_year", "year"),
    )


class ProvinceFeatures(Base):
    """Engineered features — mirrors notebook FEATURE_COLS."""
    __tablename__ = "province_features"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    province              = Column(String(100), nullable=False)
    year                  = Column(Integer,     nullable=False)
    ptr_primary_calc      = Column(Float)
    teacher_growth_rate   = Column(Float)
    enrolment_growth_rate = Column(Float)
    recruitment_gap       = Column(Float)
    teachers_per_school   = Column(Float)
    learners_per_school   = Column(Float)
    rural_school_pct      = Column(Float)
    ptr_trend_3yr         = Column(Float)
    attrition_proxy_rate  = Column(Float)
    risk_label            = Column(SmallInteger)
    computed_at           = Column(DateTime, default=datetime.utcnow)

   

    __table_args__ = (
        UniqueConstraint("province", "year", name="uq_prov_year_feat"),
        Index("idx_pf_province", "province"),
        Index("idx_pf_year", "year"),
        # FK to province_data via (province, year) — handled at app level
    )


class MLModel(Base):
    __tablename__ = "ml_models"

    model_version = Column(String(50),  primary_key=True)
    algorithm     = Column(String(100), nullable=False)
    f1_score      = Column(Float)
    recall_score  = Column(Float)
    auc_score     = Column(Float)
    lopo_auc_mean = Column(Float, nullable=True)
    lopo_auc_std  = Column(Float, nullable=True)
    trained_at    = Column(DateTime, default=datetime.utcnow)
    artefact_path = Column(String(500))
    is_active     = Column(SmallInteger, default=0)
    feature_cols  = Column(Text)   # JSON array
    notes         = Column(Text)

    predictions = relationship("ProvincePrediction",
                               back_populates="model", cascade="all, delete")


class ProvincePrediction(Base):
    """One prediction row per province per model run."""
    __tablename__ = "province_predictions"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    province             = Column(String(100), nullable=False)
    year                 = Column(Integer,     nullable=False)
    model_version        = Column(String(50),
                                  ForeignKey("ml_models.model_version",
                                             ondelete="CASCADE"), nullable=False)
    risk_score           = Column(Float, nullable=False)
    risk_label           = Column(SAEnum("high_risk", "not_at_risk"), nullable=False)
    confidence_pct       = Column(Float)
    ptr_primary_calc     = Column(Float)
    teacher_growth_rate  = Column(Float)
    recruitment_gap      = Column(Float)
    rural_school_pct     = Column(Float)
    attrition_proxy_rate = Column(Float)
    shap_json            = Column(Text)
    predicted_at         = Column(DateTime, default=datetime.utcnow)

    model = relationship("MLModel", back_populates="predictions")

    __table_args__ = (
        UniqueConstraint("province", "year", "model_version",
                         name="uq_prov_year_model"),
        Index("idx_pp_province", "province"),
        Index("idx_pp_year", "year"),
        Index("idx_pp_risk_label", "risk_label"),
    )


class User(Base):
    __tablename__ = "users"

    user_id       = Column(Integer,     primary_key=True, autoincrement=True)
    username      = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(SAEnum("district_officer", "data_admin", "viewer"),
                           default="viewer")
    province      = Column(String(100))
    created_at    = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_username", "username"),)