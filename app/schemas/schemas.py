"""
Pydantic v2 schemas — request bodies and response shapes for every endpoint.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


# ── Shared config ─────────────────────────────────────────────────────────────

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCHOOLS
# ══════════════════════════════════════════════════════════════════════════════

class SchoolCreate(BaseModel):
    school_code: str  = Field(..., max_length=20,  example="ZMB-1001")
    name:        str  = Field(..., max_length=200, example="Chongwe Primary School 1")
    district:    str  = Field(..., max_length=100, example="Chongwe")
    province:    str  = Field(..., max_length=100, example="Lusaka")
    school_type: Optional[str] = Field(None, example="Primary")
    is_rural:    Optional[int] = Field(1,    example=1)


class SchoolUpdate(BaseModel):
    name:        Optional[str] = None
    district:    Optional[str] = None
    province:    Optional[str] = None
    school_type: Optional[str] = None
    is_rural:    Optional[int] = None


class SchoolOut(ORMBase):
    school_code: str
    name:        str
    district:    str
    province:    str
    school_type: Optional[str]
    is_rural:    Optional[int]
    created_at:  Optional[datetime]


class SchoolListOut(BaseModel):
    total:   int
    schools: List[SchoolOut]


# ══════════════════════════════════════════════════════════════════════════════
# TEACHER RECORDS
# ══════════════════════════════════════════════════════════════════════════════

class TeacherRecordCreate(BaseModel):
    school_code:     str            = Field(..., example="ZMB-1001")
    year:            int            = Field(..., example=2022)
    teacher_count:   Optional[int]  = Field(None, example=24)
    qualified_count: Optional[int]  = Field(None, example=18)
    ptr:             Optional[float]= Field(None, example=42.5)
    enrolment:       Optional[int]  = Field(None, example=1020)
    attrition_est:   Optional[int]  = Field(None, example=4)


class TeacherRecordOut(ORMBase):
    record_id:       int
    school_code:     str
    year:            int
    teacher_count:   Optional[int]
    qualified_count: Optional[int]
    ptr:             Optional[float]
    enrolment:       Optional[int]
    attrition_est:   Optional[int]
    created_at:      Optional[datetime]


class TeacherTrendPoint(BaseModel):
    year:          int
    teacher_count: Optional[int]
    ptr:           Optional[float]
    attrition_est: Optional[int]


class SchoolTrendOut(BaseModel):
    school_code: str
    school_name: str
    province:    str
    district:    str
    trend:       List[TeacherTrendPoint]


class ProvinceTrendPoint(BaseModel):
    year:          int
    total_teachers: int
    avg_ptr:       Optional[float]


class ProvinceTrendOut(BaseModel):
    province: str
    trend:    List[ProvinceTrendPoint]


# ══════════════════════════════════════════════════════════════════════════════
# RISK PREDICTIONS
# ══════════════════════════════════════════════════════════════════════════════

class PredictionCreate(BaseModel):
    school_code:    str   = Field(..., example="ZMB-1001")
    model_version:  str   = Field(..., example="xgb_v1.0")
    risk_score:     float = Field(..., ge=0.0, le=1.0, example=0.82)
    risk_label:     str   = Field(..., example="high_risk")
    shap_json:      Optional[str]   = None
    confidence_pct: Optional[float] = Field(None, example=82.3)


class PredictionOut(ORMBase):
    prediction_id:  int
    school_code:    str
    model_version:  str
    risk_score:     float
    risk_label:     str
    shap_json:      Optional[str]
    confidence_pct: Optional[float]
    predicted_at:   Optional[datetime]


class RiskSummaryItem(BaseModel):
    school_code:  str
    school_name:  str
    province:     str
    district:     str
    school_type:  Optional[str]
    is_rural:     Optional[int]
    risk_score:   float
    risk_label:   str
    confidence_pct: Optional[float]
    predicted_at: Optional[datetime]


class NationalSummaryOut(BaseModel):
    total_schools:     int
    high_risk:         int
    not_at_risk:       int
    high_risk_pct:     float
    avg_risk_score:    float
    provinces_flagged: int
    active_model:      Optional[str]


class ProvinceSummaryItem(BaseModel):
    province:    str
    total:       int
    high_risk:   int
    not_at_risk: int
    avg_score:   float


# ══════════════════════════════════════════════════════════════════════════════
# ML MODELS
# ══════════════════════════════════════════════════════════════════════════════

class MLModelCreate(BaseModel):
    model_version: str           = Field(..., example="xgb_v1.1")
    algorithm:     str           = Field(..., example="XGBoost")
    f1_score:      Optional[float] = None
    recall_score:  Optional[float] = None
    auc_score:     Optional[float] = None
    artefact_path: Optional[str]   = None
    is_active:     Optional[int]   = Field(0, example=0)
    notes:         Optional[str]   = None


class MLModelOut(ORMBase):
    model_version: str
    algorithm:     str
    f1_score:      Optional[float]
    recall_score:  Optional[float]
    auc_score:     Optional[float]
    trained_at:    Optional[datetime]
    artefact_path: Optional[str]
    is_active:     Optional[int]
    notes:         Optional[str]


# ══════════════════════════════════════════════════════════════════════════════
# USERS / AUTH
# ══════════════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, example="florence.kabeya")
    password: str = Field(..., min_length=8,                 example="SecurePass123!")
    role:     Optional[str] = Field("viewer", example="district_officer")
    province: Optional[str] = Field(None,     example="Lusaka")


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
    username: str = Field(..., example="florence.kabeya")
    password: str = Field(..., example="SecurePass123!")


# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

class UploadResultOut(BaseModel):
    rows_processed: int
    rows_inserted:  int
    rows_skipped:   int
    errors:         List[str]


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC
# ══════════════════════════════════════════════════════════════════════════════

class MessageOut(BaseModel):
    message: str

class HealthOut(BaseModel):
    status:   str
    database: str
    model:    Optional[str]
