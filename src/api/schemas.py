"""
Pydantic v2 schemas — request validation and response serialisation.
"""
 
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
 
 
# ── Enums ──────────────────────────────────────────────────────────────────────
 
class RiskLabelEnum(str, Enum):
    HIGH_RISK   = "high_risk"
    NOT_AT_RISK = "not_at_risk"
 
 
# ── School schemas ─────────────────────────────────────────────────────────────
 
class SchoolBase(BaseModel):
    school_code : str   = Field(..., example="CHO_001")
    name        : str   = Field(..., example="Chongwe Basic School")
    district    : str   = Field(..., example="Chongwe")
    province    : str   = Field(..., example="Lusaka")
    school_type : Optional[str] = Field(None, example="GRZ")
    is_rural    : bool  = Field(True)
 
class SchoolCreate(SchoolBase):
    pass
 
class SchoolResponse(SchoolBase):
    created_at: datetime
    model_config = {"from_attributes": True}
 
 
# ── Teacher record schemas ─────────────────────────────────────────────────────
 
class TeacherRecordBase(BaseModel):
    school_code     : str   = Field(..., example="CHO_001")
    year            : int   = Field(..., ge=2000, le=2100, example=2022)
    teacher_count   : int   = Field(..., ge=0, example=18)
    qualified_count : int   = Field(..., ge=0, example=14)
    ptr             : float = Field(..., ge=0, example=32.5)
    enrolment       : int   = Field(..., ge=0, example=585)
    attrition_est   : Optional[int] = Field(None, example=3)
 
    @field_validator("qualified_count")
    @classmethod
    def qualified_lte_total(cls, v, info):
        if "teacher_count" in info.data and v > info.data["teacher_count"]:
            raise ValueError("qualified_count cannot exceed teacher_count")
        return v
 
class TeacherRecordCreate(TeacherRecordBase):
    pass
 
class TeacherRecordResponse(TeacherRecordBase):
    record_id  : int
    created_at : datetime
    model_config = {"from_attributes": True}
 
 
# ── Prediction schemas ─────────────────────────────────────────────────────────
 
class PredictionRequest(BaseModel):
    """Input features for a single school prediction."""
    school_code         : str   = Field(..., example="CHO_001")
    ptr_deviation       : float = Field(..., example=0.45,  description="PTR z-score vs national mean")
    qualification_gap   : float = Field(..., ge=0, le=1, example=0.22, description="Proportion of unqualified teachers")
    rural_isolation     : float = Field(..., ge=0, le=1, example=0.74, description="Rural school proportion in province")
    teacher_delta_pct   : float = Field(..., example=-18.5, description="YoY teacher headcount change (%)")
    enrolment_growth    : float = Field(..., example=4.2,   description="YoY enrolment growth rate (%)")
    pressure_gap        : float = Field(..., example=5.8,   description="Enrolment growth minus teacher growth")
    attrition_rate      : float = Field(..., example=7.2,   description="Attrition as % of total teachers")
    is_secondary        : int   = Field(..., ge=0, le=1, example=0, description="0=Primary, 1=Secondary")
 
class SHAPEntry(BaseModel):
    feature     : str
    shap_value  : float
    feature_value: float
 
class PredictionResponse(BaseModel):
    school_code     : str
    risk_label      : RiskLabelEnum
    risk_score      : float = Field(..., description="Probability of high risk (0–1)")
    confidence_pct  : float = Field(..., description="Risk score as percentage")
    shap_explanation: list[SHAPEntry]
    model_version   : str
    predicted_at    : datetime
    plain_language_summary: str
 
class BatchPredictionRequest(BaseModel):
    records: list[PredictionRequest] = Field(..., min_length=1, max_length=200)
 
class BatchPredictionResponse(BaseModel):
    total           : int
    high_risk_count : int
    predictions     : list[PredictionResponse]
    model_version   : str
 
 
# ── Data upload schemas ────────────────────────────────────────────────────────
 
class UploadResponse(BaseModel):
    message         : str
    rows_processed  : int
    high_risk_count : int
    model_version   : str
 
 
# ── Model info schemas ─────────────────────────────────────────────────────────
 
class ModelInfoResponse(BaseModel):
    model_version : str
    algorithm     : str
    f1_score      : Optional[float]
    recall_score  : Optional[float]
    auc_score     : Optional[float]
    trained_at    : datetime
    is_active     : bool
    model_config  = {"from_attributes": True}
 
 
# ── Health schema ──────────────────────────────────────────────────────────────
 
class HealthResponse(BaseModel):
    status      : str
    api_version : str
    model_loaded: bool
    db_connected: bool