"""
ML inference service.
Loads the trained XGBoost model at startup and exposes predict() + explain().
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import shap
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
MODEL_DIR   = Path(os.getenv("MODEL_DIR", "models"))
MODEL_PATH  = MODEL_DIR / "xgboost_attrition_model.pkl"
SCALER_PATH = MODEL_DIR / "feature_scaler.pkl"
FEATURES_PATH = MODEL_DIR / "feature_cols.json"
MODEL_VERSION = os.getenv("MODEL_VERSION", "xgb_v1.0")

FEATURE_COLS = [
    "ptr_deviation",
    "qualification_gap",
    "rural_isolation",
    "teacher_delta_pct",
    "enrolment_growth",
    "pressure_gap",
    "attrition_rate",
    "is_secondary",
]

FEATURE_LABELS = {
    "ptr_deviation":      "PTR deviation from national mean",
    "qualification_gap":  "Unqualified teacher proportion",
    "rural_isolation":    "Rural school proportion",
    "teacher_delta_pct":  "YoY teacher headcount change (%)",
    "enrolment_growth":   "Enrolment growth rate (%)",
    "pressure_gap":       "Enrolment-teacher pressure gap",
    "attrition_rate":     "Estimated attrition rate (%)",
    "is_secondary":       "Secondary school flag",
}


class ModelService:
    """Singleton-style service — instantiated once at module level."""

    def __init__(self):
        self.model     = None
        self.scaler    = None
        self.explainer = None
        self.feature_cols = FEATURE_COLS
        self._loaded   = False
        self._load()

    def _load(self):
        try:
            if not MODEL_PATH.exists():
                logger.warning(
                    f"Model not found at {MODEL_PATH}. "
                    "Run the notebook to train and export the model first. "
                    "API will return placeholder predictions until model is loaded."
                )
                return

            self.model   = joblib.load(MODEL_PATH)
            self.explainer = shap.TreeExplainer(self.model)

            if SCALER_PATH.exists():
                self.scaler = joblib.load(SCALER_PATH)

            if FEATURES_PATH.exists():
                with open(FEATURES_PATH) as f:
                    self.feature_cols = json.load(f)

            self._loaded = True
            logger.info(f"Model loaded from {MODEL_PATH} (version: {MODEL_VERSION})")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def is_ready(self) -> bool:
        return self._loaded

    def predict(self, features: dict) -> dict:
        """
        Run prediction for a single record.
        Returns: risk_score, risk_label, shap_explanation, plain_language_summary
        """
        if not self._loaded:
            return self._placeholder_prediction(features)

        X = pd.DataFrame([features])[self.feature_cols]
        X = X.fillna(X.median())

        prob = float(self.model.predict_proba(X)[0][1])
        label = "high_risk" if prob >= 0.5 else "not_at_risk"

        # SHAP explanation
        shap_vals = self.explainer.shap_values(X)
        shap_entries = [
            {
                "feature":       self.feature_cols[i],
                "shap_value":    float(shap_vals[0][i]),
                "feature_value": float(X.iloc[0, i]),
            }
            for i in range(len(self.feature_cols))
        ]
        # Sort by absolute SHAP value descending
        shap_entries.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        summary = self._plain_language_summary(prob, shap_entries, features)

        return {
            "risk_score":          prob,
            "risk_label":          label,
            "confidence_pct":      round(prob * 100, 1),
            "shap_explanation":    shap_entries,
            "model_version":       MODEL_VERSION,
            "predicted_at":        datetime.now(timezone.utc),
            "plain_language_summary": summary,
        }

    def predict_batch(self, records: list[dict]) -> list[dict]:
        """Run predictions for a list of records."""
        return [self.predict(r) for r in records]

    def _plain_language_summary(self, prob: float, shap_entries: list, features: dict) -> str:
        """Generate a plain-language explanation for district officers."""
        level = "HIGH" if prob >= 0.5 else "LOW"
        top_factors = [
            FEATURE_LABELS.get(e["feature"], e["feature"])
            for e in shap_entries[:3]
            if e["shap_value"] > 0
        ]

        if not top_factors:
            top_factors = [FEATURE_LABELS.get(shap_entries[0]["feature"], shap_entries[0]["feature"])]

        factors_str = "; ".join(top_factors)
        delta = features.get("teacher_delta_pct", 0)

        summary = (
            f"This school is classified as {level} RISK (probability: {prob:.0%}). "
            f"Teacher headcount changed by {delta:+.1f}% year-on-year. "
            f"Key contributing factors: {factors_str}."
        )
        if prob >= 0.5:
            summary += (
                " Recommend prioritising this school for a retention support visit "
                "before the next school term."
            )
        return summary

    def _placeholder_prediction(self, features: dict) -> dict:
        """Returned when model file is not yet available (pre-training)."""
        return {
            "risk_score":          0.0,
            "risk_label":          "not_at_risk",
            "confidence_pct":      0.0,
            "shap_explanation":    [],
            "model_version":       "model_not_loaded",
            "predicted_at":        datetime.now(timezone.utc),
            "plain_language_summary": (
                "Model not loaded. Please train and export the model from the notebook first."
            ),
        }


# Module-level singleton
model_service = ModelService()
