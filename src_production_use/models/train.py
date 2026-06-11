"""
src/models/train.py

Standalone training script. Runs the full pipeline:
  ingest → clean → feature engineering → SMOTE → benchmark → tune → export

Can be run directly:
    python src/models/train.py

Or imported from the notebook after modifying hyperparameter ranges.
All runs are logged to MLflow (mlruns/ folder at repo root).
"""

import os
import json
import logging
from pathlib import Path

import joblib
import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
)
import xgboost as xgb

from src.data.ingest import load_bulletin
from src.data.clean import clean_bulletin
from src.features.engineer import build_features, FEATURE_COLS

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

RANDOM_STATE      = 42
TEST_SIZE         = 0.30
ATTRITION_THRESH  = -15.0
MODEL_DIR         = Path(os.getenv("MODEL_DIR", "models"))
MODEL_VERSION     = os.getenv("MODEL_VERSION", "xgb_v1.0")

# XGBoost hyperparameter search space
PARAM_DIST = {
    "n_estimators":     [50, 100, 200, 300, 500],
    "max_depth":        [3, 4, 5, 6, 7, 8],
    "learning_rate":    [0.01, 0.05, 0.1, 0.2, 0.3],
    "subsample":        [0.6, 0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
    "min_child_weight": [1, 3, 5],
    "gamma":            [0, 0.1, 0.2],
}


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load, clean, and engineer features."""
    df_raw     = load_bulletin()
    df_clean   = clean_bulletin(df_raw)
    X, y       = build_features(df_clean, threshold=ATTRITION_THRESH)
    return X, y


def benchmark_models(X_train, y_train, X_test, y_test, scaler) -> pd.DataFrame:
    """Train all 5 models and return a results DataFrame."""
    models = {
        "Logistic Regression": LogisticRegression(
            random_state=RANDOM_STATE, max_iter=500, class_weight="balanced"
        ),
        "Decision Tree": DecisionTreeClassifier(
            random_state=RANDOM_STATE, max_depth=4, class_weight="balanced"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, random_state=RANDOM_STATE, class_weight="balanced"
        ),
        "SVM (RBF)": SVC(
            kernel="rbf", probability=True, random_state=RANDOM_STATE, class_weight="balanced"
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=100, random_state=RANDOM_STATE, eval_metric="logloss",
            scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
        ),
    }

    results = {}
    linear_models = {"Logistic Regression", "Decision Tree", "SVM (RBF)"}

    for name, model in models.items():
        Xtr = scaler.transform(X_train) if name in linear_models else X_train
        Xte = scaler.transform(X_test)  if name in linear_models else X_test
        model.fit(Xtr, y_train)
        y_pred = model.predict(Xte)
        y_prob = model.predict_proba(Xte)[:, 1] if hasattr(model, "predict_proba") else None
        results[name] = {
            "recall":    recall_score(y_test, y_pred, zero_division=0),
            "f1":        f1_score(y_test, y_pred, zero_division=0),
            "auc":       roc_auc_score(y_test, y_prob) if y_prob is not None else np.nan,
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "accuracy":  accuracy_score(y_test, y_pred),
        }
        logger.info(f"  {name}: recall={results[name]['recall']:.3f}  f1={results[name]['f1']:.3f}")

    return pd.DataFrame(results).T


def tune_xgboost(X_train, y_train, X_test, y_test) -> tuple:
    """RandomizedSearchCV over XGBoost and log to MLflow."""
    mlflow.set_experiment("teacher_attrition_ews")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    base = xgb.XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE)
    rscv = RandomizedSearchCV(
        base, PARAM_DIST, n_iter=50, scoring="recall",
        cv=cv, n_jobs=-1, random_state=RANDOM_STATE, verbose=0,
    )

    with mlflow.start_run(run_name="xgboost_randomized_search"):
        rscv.fit(X_train, y_train)
        best = rscv.best_estimator_

        mlflow.log_params(rscv.best_params_)

        y_pred = best.predict(X_test)
        y_prob = best.predict_proba(X_test)[:, 1]
        metrics = {
            "test_recall":    recall_score(y_test, y_pred, zero_division=0),
            "test_f1":        f1_score(y_test, y_pred, zero_division=0),
            "test_auc":       roc_auc_score(y_test, y_prob),
            "test_precision": precision_score(y_test, y_pred, zero_division=0),
            "test_accuracy":  accuracy_score(y_test, y_pred),
        }
        mlflow.log_metrics(metrics)
        mlflow.xgboost.log_model(best, "best_xgboost_model")

    return best, metrics


def save_artefacts(model, scaler):
    """Persist model, scaler, and feature list to MODEL_DIR."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model,  MODEL_DIR / "xgboost_attrition_model.pkl")
    joblib.dump(scaler, MODEL_DIR / "feature_scaler.pkl")
    with open(MODEL_DIR / "feature_cols.json", "w") as f:
        json.dump(FEATURE_COLS, f, indent=2)
    logger.info(f"Artefacts saved to {MODEL_DIR}/")


def run():
    np.random.seed(RANDOM_STATE)
    logger.info("Loading data...")
    X, y = load_data()

    logger.info(f"Dataset: {len(X)} records | {y.sum()} high-risk ({y.mean():.1%})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # SMOTE
    k = max(1, min(3, y_train.sum() - 1))
    smote = SMOTE(random_state=RANDOM_STATE, k_neighbors=k)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    # Scaler (for linear models in benchmark; XGBoost uses unscaled)
    scaler = StandardScaler()
    scaler.fit(X_train_res)

    logger.info("Benchmarking all models...")
    benchmark_df = benchmark_models(X_train_res, y_train_res, X_test, y_test, scaler)
    print("\n=== Benchmark Results ===")
    print(benchmark_df.sort_values("recall", ascending=False).round(4).to_string())

    logger.info("Tuning XGBoost (50 iterations, 5-fold CV)...")
    best_model, metrics = tune_xgboost(X_train_res, y_train_res, X_test, y_test)

    print("\n=== Tuned XGBoost — Test Set ===")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_artefacts(best_model, scaler)
    logger.info("Training complete.")
    return best_model, metrics


if __name__ == "__main__":
    run()
