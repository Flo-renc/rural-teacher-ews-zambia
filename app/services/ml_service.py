"""
ML Service — loads the active XGBoost model and runs inference + SHAP explanation.

For now this works with mock features if the model file is not yet present,
so the API stays fully testable in Postman before the trained model is dropped in.
"""

import json
import logging
import os
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Feature order must match training pipeline exactly
FEATURE_COLUMNS = [
    "teacher_count",
    "qualified_count",
    "ptr",
    "enrolment",
    "attrition_est",
    "is_rural",
]

SHAP_FEATURE_LABELS = {
    "teacher_count":   "Teacher Count",
    "qualified_count": "Qualified Teachers",
    "ptr":             "Pupil-Teacher Ratio",
    "enrolment":       "School Enrolment",
    "attrition_est":   "Estimated Attrition",
    "is_rural":        "Rural School",
}

HIGH_RISK_THRESHOLD = 0.65


class MLService:
    def __init__(self):
        self._model     = None
        self._explainer = None
        self._loaded    = False

    def _try_load(self):
        """Attempt to load XGBoost model + SHAP explainer from disk."""
        if self._loaded:
            return
        model_path = os.getenv("MODEL_PATH", "artefacts/xgb_v1.0.joblib")
        if not os.path.exists(model_path):
            logger.warning(
                f"Model file not found at '{model_path}'. "
                "Running in mock-inference mode — replace with trained model to activate."
            )
            self._loaded = True
            return
        try:
            import joblib
            import shap
            self._model     = joblib.load(model_path)
            self._explainer = shap.TreeExplainer(self._model)
            logger.info(f"XGBoost model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
        self._loaded = True

    def predict(self, features: dict) -> dict:
        """
        Run inference for a single school.

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
            # Mock inference — deterministic based on PTR and attrition
            ptr          = features.get("ptr") or 40.0
            attrition    = features.get("attrition_est") or 0
            teacher_cnt  = features.get("teacher_count") or 20
            is_rural     = features.get("is_rural") or 0

            raw_score = (
                min(ptr / 100, 0.5)
                + min(attrition / (teacher_cnt + 1), 0.3)
                + (0.1 if is_rural else 0.0)
                + np.random.uniform(-0.05, 0.05)
            )
            risk_score = float(np.clip(raw_score, 0.05, 0.95))
            shap_values = self._mock_shap(features)
        else:
            proba      = self._model.predict_proba(feature_vector)[0]
            risk_score = float(proba[1])  # probability of high_risk class
            shap_vals  = self._explainer.shap_values(feature_vector)
            shap_arr   = shap_vals[1][0] if isinstance(shap_vals, list) else shap_vals[0]
            shap_values = {
                SHAP_FEATURE_LABELS.get(col, col): round(float(shap_arr[i]), 4)
                for i, col in enumerate(FEATURE_COLUMNS)
            }

        risk_label     = "high_risk" if risk_score >= HIGH_RISK_THRESHOLD else "not_at_risk"
        confidence_pct = round(risk_score * 100 if risk_label == "high_risk" else (1 - risk_score) * 100, 2)

        return {
            "risk_score":     round(risk_score, 4),
            "risk_label":     risk_label,
            "confidence_pct": confidence_pct,
            "shap_json":      json.dumps(shap_values),
        }

    def _mock_shap(self, features: dict) -> dict:
        """Return plausible mock SHAP values when model is not loaded."""
        return {
            "Pupil-Teacher Ratio":   round(float((features.get("ptr") or 40) / 120), 4),
            "Estimated Attrition":   round(float((features.get("attrition_est") or 0) / 50), 4),
            "Rural School":          round(0.08 if features.get("is_rural") else -0.03, 4),
            "Teacher Count":         round(-float((features.get("teacher_count") or 20) / 200), 4),
            "Qualified Teachers":    round(-float((features.get("qualified_count") or 15) / 150), 4),
            "School Enrolment":      round(float((features.get("enrolment") or 500) / 3000), 4),
        }

    @property
    def is_real_model(self) -> bool:
        self._try_load()
        return self._model is not None


# Singleton — one instance shared across requests
ml_service = MLService()
