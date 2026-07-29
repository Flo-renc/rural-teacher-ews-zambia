"""
ML Service — province-level XGBoost inference + SHAP.

Feature columns match the notebook FEATURE_COLS exactly:
  ptr_primary_calc, teacher_growth_rate, enrolment_growth_rate,
  recruitment_gap, teachers_per_school, learners_per_school,
  rural_school_pct, ptr_trend_3yr

The feature builder requires the current year record and the
prior year record to compute growth rates and gaps.
"""
import os
import json
from pyexpat import features
import traceback
import joblib
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Model artefacts are stored in the ml_models/ directory, which is not tracked by git.

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = Path(
    os.getenv(
        "MODEL_PATH",
        BASE_DIR / "ml_models" / "xgb_v1.0.joblib"
    )
)

FEATURE_PATH = Path(
    BASE_DIR / "ml_models" / "feature_columns.json"
)

METADATA_PATH = Path(
    BASE_DIR / "ml_models" / "model_metadata.json"
)

# ── Must match notebook FEATURE_COLS order exactly ────────────
FEATURE_COLUMNS = [
    "ptr_primary_calc",
    "teacher_growth_rate",
    "enrolment_growth_rate",
    "recruitment_gap",
    "teachers_per_school",
    "learners_per_school",
    "rural_school_pct",
    "ptr_trend_3yr",
]

FEATURE_LABELS = {
    "ptr_primary_calc":        "PTR — Primary (Gr 1-7)",
    "teacher_growth_rate":     "Teacher Growth Rate (YoY %)",
    "enrolment_growth_rate":   "Enrolment Growth Rate (YoY %)",
    "recruitment_gap":         "Recruitment Gap (Enrolment−Teacher Growth)",
    "teachers_per_school":     "Teachers per School",
    "learners_per_school":     "Learners per School",
    "rural_school_pct":        "Rural School %",
    "ptr_trend_3yr":           "PTR Trend (3-Year Rolling Avg)",
}

HIGH_RISK_THRESHOLD = 0.65


def build_feature_vector(
    record:       dict,
    prior:        dict | None,
    two_years_ago: dict | None = None,
) -> dict:
    """
    Build the feature vector for one province-year.

    Args:
        record        : current year province_data row as dict
        prior         : previous year province_data row (for growth rates)
        two_years_ago : two years prior (for ptr_trend_3yr)

    Returns:
        dict with keys matching FEATURE_COLUMNS order
    """
    tc  = record.get("teacher_count_primary")  or 1
    enr = record.get("student_enrolment_primary") or 0
    sch = record.get("primary_schools")        or 1
    rur = record.get("rural_schools")          or 0
    urb = record.get("urban_schools")          or 1

    ptr = enr / tc

    if prior:
        tc_p   = prior.get("teacher_count_primary")     or 1
        enr_p  = prior.get("student_enrolment_primary") or 1
        tgr    = (tc  - tc_p)  / tc_p  * 100
        egr    = (enr - enr_p) / enr_p * 100
        gap    = egr - tgr
        ptr_p  = enr_p / tc_p
    else:
        tgr = egr = gap = 0.0
        ptr_p = ptr

    # 3-year rolling PTR average
    if two_years_ago:
        tc_pp  = two_years_ago.get("teacher_count_primary")     or 1
        enr_pp = two_years_ago.get("student_enrolment_primary") or 1
        ptr_pp = enr_pp / tc_pp
        ptr_3yr = (ptr + ptr_p + ptr_pp) / 3
    elif prior:
        ptr_3yr = (ptr + ptr_p) / 2
    else:
        ptr_3yr = ptr

    rural_pct = rur / (rur + urb) if (rur + urb) > 0 else 0.0

    return {
        "ptr_primary_calc":        round(ptr,      4),
        "teacher_growth_rate":     round(tgr,      4),
        "enrolment_growth_rate":   round(egr,      4),
        "recruitment_gap":         round(gap,      4),
        "teachers_per_school":     round(tc / sch, 4),
        "learners_per_school":     round(enr / sch,4),
        "rural_school_pct":        round(rural_pct,4),
        "ptr_trend_3yr":           round(ptr_3yr,  4),
    }


class MLService:
    def __init__(self):
        self._model     = None
        self._explainer = None
        self._loaded    = False

    def _try_load(self):
        if self._loaded:
            return

        model_path = MODEL_PATH  # use the actual Path object

        logger.info(f"Loading ML model from {model_path}")

        if not model_path.exists():
            logger.warning(
                f"Model not found at '{model_path}'. "
                "Running in mock-inference mode."
            )
            self._loaded = True
            return

        try:
            import shap
            self._model = joblib.load(model_path)

            logger.info(f"Model loaded successfully from {type(self._model)}")

            try:

                self._explainer = shap.TreeExplainer(self._model)
                logger.info("SHAP explainer initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize SHAP explainer: {e}")
                self._explainer = None
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            import traceback
            traceback.print_exc()

        self._loaded = True

    def predict(self, features: dict) -> dict:
        """
        Run inference for one province-year.

        Args:
            features: dict with keys matching FEATURE_COLUMNS

        Returns:
            dict with risk_score, risk_label, confidence_pct, shap_json
        """
        self._try_load()

        feature_vector = np.array(
            [features.get(col, 0) or 0 for col in FEATURE_COLUMNS],
            dtype=float,
        ).reshape(1, -1)

        if self._model is None:
            # Mock inference — deterministic on feature values
            ptr    = features.get("ptr_primary_calc") or 45.0
            tgr    = features.get("teacher_growth_rate") or 0.0
            gap    = features.get("recruitment_gap") or 0.0
            rural  = features.get("rural_school_pct") or 0.5
            raw    = (
                min(ptr / 150, 0.35)
                + (0.25 if tgr < 0 else 0.0)
                + min(max(gap, 0) / 40, 0.20)
                + rural * 0.15
                + np.random.uniform(-0.05, 0.05)
            )
            risk_score  = float(np.clip(raw, 0.05, 0.95))
            shap_values = self._mock_shap(features)
        else:
            risk_score  = float(self._model.predict_proba(feature_vector)[0, 1])
            if self._explainer is not None:

                sv = self._explainer.shap_values(
                feature_vector
               )

                shap_arr = (
                    sv[0]
                    if isinstance(sv, list)
                    else sv[0]
                )

                shap_values = {
                    FEATURE_LABELS[FEATURE_COLUMNS[i]]:
                    round(float(shap_arr[i]),4)
                    for i in range(len(FEATURE_COLUMNS))
                }

            else:

                logger.warning(
                    "Using fallback SHAP values"
            )

            shap_values = self._mock_shap(features)

        risk_label     = "high_risk" if risk_score >= HIGH_RISK_THRESHOLD else "not_at_risk"
        confidence_pct = round(
            risk_score * 100 if risk_label == "high_risk"
            else (1 - risk_score) * 100, 2
        )
        return {
            "risk_score":     round(risk_score, 4),
            "risk_label":     risk_label,
            "confidence_pct": confidence_pct,
            "shap_json":      json.dumps(shap_values),
        }

    def _mock_shap(self, features: dict) -> dict:
        return {
            FEATURE_LABELS["ptr_primary_calc"]:       round((features.get("ptr_primary_calc") or 45) / 150, 4),
            FEATURE_LABELS["teacher_growth_rate"]:    round(-(features.get("teacher_growth_rate") or 0) / 50, 4),
            FEATURE_LABELS["enrolment_growth_rate"]:  round((features.get("enrolment_growth_rate") or 0) / 100, 4),
            FEATURE_LABELS["recruitment_gap"]:        round((features.get("recruitment_gap") or 0) / 50, 4),
            FEATURE_LABELS["teachers_per_school"]:    round(-(features.get("teachers_per_school") or 8) / 50, 4),
            FEATURE_LABELS["learners_per_school"]:    round((features.get("learners_per_school") or 300) / 2000, 4),
            FEATURE_LABELS["rural_school_pct"]:       round((features.get("rural_school_pct") or 0.5) * 0.2, 4),
            FEATURE_LABELS["ptr_trend_3yr"]:          round((features.get("ptr_trend_3yr") or 45) / 200, 4),
        }

    @property
    def is_real_model(self) -> bool:
        self._try_load()
        return self._model is not None


ml_service = MLService()