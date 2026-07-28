"""
Pydantic v2 schemas for all request/response shapes.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Province Data ─────────────────────────────────────────────

class ProvinceDataCreate(BaseModel):
    province:                  str   = Field(..., example="Eastern")
    year:                      int   = Field(..., example=2023)
    teacher_count_primary:     Optional[int]   = None
    student_enrolment_primary: Optional[int]   = None
    ptr_primary_bulletin:      Optional[float] = None
    primary_schools:           Optional[int]   = None
    rural_schools:             Optional[int]   = None
    urban_schools:             Optional[int]   = None


class ProvinceDataOut(ORMBase):
    id:                        int
    province:                  str
    year:                      int
    teacher_count_primary:     Optional[int]
    student_enrolment_primary: Optional[int]
    ptr_primary_bulletin:      Optional[float]
    primary_schools:           Optional[int]
    rural_schools:             Optional[int]
    urban_schools:             Optional[int]
    created_at:                Optional[datetime]


# ── Province Features ─────────────────────────────────────────

class ProvinceFeaturesOut(ORMBase):
    province:              str
    year:                  int
    ptr_primary_calc:      Optional[float]
    teacher_growth_rate:   Optional[float]
    enrolment_growth_rate: Optional[float]
    recruitment_gap:       Optional[float]
    teachers_per_school:   Optional[float]
    learners_per_school:   Optional[float]
    rural_school_pct:      Optional[float]
    ptr_trend_3yr:         Optional[float]
    attrition_proxy_rate:  Optional[float]
    risk_label:            Optional[int]
    computed_at:           Optional[datetime]


# ── Predictions ───────────────────────────────────────────────

class PredictionOut(ORMBase):
    id:                   int
    province:             str
    year:                 int
    model_version:        str
    risk_score:           float
    risk_label:           str
    confidence_pct:       Optional[float]
    ptr_primary_calc:     Optional[float]
    teacher_growth_rate:  Optional[float]
    recruitment_gap:      Optional[float]
    rural_school_pct:     Optional[float]
    attrition_proxy_rate: Optional[float]
    shap_json:            Optional[str]
    predicted_at:         Optional[datetime]


class NationalSummaryOut(BaseModel):
    total_provinces:    int
    high_risk:          int
    not_at_risk:        int
    high_risk_pct:      float
    avg_risk_score:     float
    prediction_year:    int
    active_model:       Optional[str]
    lopo_auc:           Optional[float]


class ProvinceSummaryItem(BaseModel):
    province:        str 
    year:            int 
    risk_score:      float
    risk_label:      str
    confidence_pct:  Optional[float]
    ptr_primary_calc: Optional[float]
    teacher_growth_rate: Optional[float]
    recruitment_gap: Optional[float]
    rural_school_pct: Optional[float]
    attrition_proxy_rate: Optional[float]
    predicted_at:    Optional[datetime]


class SHAPOut(BaseModel):
    province:     str
    year:         int
    risk_score:   float
    risk_label:   str
    predicted_at: Optional[datetime]
    shap_values:  dict


# ── ML Models ─────────────────────────────────────────────────

class MLModelOut(ORMBase):
    model_version: str
    algorithm:     str
    f1_score:      Optional[float]
    recall_score:  Optional[float]
    auc_score:     Optional[float]
    lopo_auc_mean: Optional[float]
    lopo_auc_std:  Optional[float]
    trained_at:    Optional[datetime]
    is_active:     Optional[int]
    notes:         Optional[str]


# ── Auth ──────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, example="florence.kabeya")
    password: str = Field(..., min_length=8, example="SecurePass123!")
    role:     Optional[str] = Field("viewer", example="data_admin")
    province: Optional[str] = None


class UserOut(ORMBase):
    user_id:    int
    username:   str
    role:       Optional[str]
    province:   Optional[str]
    created_at: Optional[datetime]


class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


# ── Upload ────────────────────────────────────────────────────

class UploadResultOut(BaseModel):
    rows_processed: int
    rows_inserted:  int
    rows_updated:   int
    rows_skipped:   int
    errors:         List[str]


# ── Generic ───────────────────────────────────────────────────

class MessageOut(BaseModel):
    message: str


class HealthOut(BaseModel):
    status:        str
    database:      str
    active_model:  Optional[str]
    lopo_auc:      Optional[float]
    real_model:    bool