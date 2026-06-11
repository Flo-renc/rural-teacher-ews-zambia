"""
src/models/evaluate.py

Evaluation utilities: classification metrics, fairness analysis,
confusion matrix, ROC curve, and SHAP summary.

Usage:
    from src.models.evaluate import full_evaluation_report
    report = full_evaluation_report(model, X_test, y_test, df_test)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    f1_score, precision_score, recall_score, accuracy_score,
    ConfusionMatrixDisplay, RocCurveDisplay,
)
import shap
import logging

logger = logging.getLogger(__name__)


def compute_metrics(y_true, y_pred, y_prob=None) -> dict:
    """Return a flat dict of all evaluation metrics."""
    metrics = {
        "accuracy":  accuracy_score(y_true, y_pred),
        "recall":    recall_score(y_true, y_pred, zero_division=0),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "f1":        f1_score(y_true, y_pred, zero_division=0),
    }
    if y_prob is not None:
        metrics["auc"] = roc_auc_score(y_true, y_prob)
    return {k: round(v, 4) for k, v in metrics.items()}


def fairness_analysis(X_test, y_test, y_pred, df_meta, group_cols: list) -> pd.DataFrame:
    """
    Equalized odds evaluation.
    For each group column, compute recall (TPR) and FPR per group.

    Args:
        X_test:     Feature matrix (test split).
        y_test:     True labels.
        y_pred:     Predicted labels.
        df_meta:    Full DataFrame with metadata columns (province, level, etc.)
        group_cols: List of columns to disaggregate by, e.g. ['level', 'rural_group']

    Returns:
        DataFrame with columns: group_col, group_value, n, recall, fpr
    """
    meta = df_meta.loc[X_test.index].copy()
    meta["y_true"] = y_test.values
    meta["y_pred"] = y_pred

    # Add rural group
    if "rural_isolation" in meta.columns:
        meta["rural_group"] = meta["rural_isolation"].apply(
            lambda x: "Predominantly Rural (>70%)" if x > 0.70 else "Mixed/Urban"
        )

    rows = []
    for col in group_cols:
        if col not in meta.columns:
            continue
        for group in meta[col].unique():
            sub = meta[meta[col] == group]
            if sub["y_true"].sum() == 0:
                continue
            tpr = recall_score(sub["y_true"], sub["y_pred"], zero_division=0)
            fpr = (
                ((sub["y_pred"] == 1) & (sub["y_true"] == 0)).sum() /
                max((sub["y_true"] == 0).sum(), 1)
            )
            rows.append({
                "group_col":   col,
                "group_value": group,
                "n":           len(sub),
                "recall_tpr":  round(tpr, 3),
                "fpr":         round(fpr, 3),
            })

    return pd.DataFrame(rows)


def plot_confusion_and_roc(model, X_test, y_test, save_path: str = None):
    """Plot confusion matrix and ROC curve side by side."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ConfusionMatrixDisplay(
        confusion_matrix(y_test, y_pred),
        display_labels=["Not At Risk", "High Risk"]
    ).plot(ax=axes[0], cmap="Blues", colorbar=False)
    axes[0].set_title("Confusion Matrix — Tuned XGBoost", fontweight="bold")

    RocCurveDisplay.from_predictions(y_test, y_prob, ax=axes[1], name="XGBoost (tuned)")
    axes[1].plot([0, 1], [0, 1], "k--", alpha=0.5)
    axes[1].set_title("ROC Curve — Tuned XGBoost", fontweight="bold")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_shap_summary(model, X_test, feature_cols: list, save_path: str = None):
    """Global SHAP bar chart and beeswarm."""
    explainer  = shap.TreeExplainer(model)
    shap_vals  = explainer.shap_values(X_test)

    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    plt.sca(axes[0])
    shap.summary_plot(shap_vals, X_test, plot_type="bar",
                      feature_names=feature_cols, show=False)
    axes[0].set_title("SHAP — Global Feature Importance", fontweight="bold")

    plt.sca(axes[1])
    shap.summary_plot(shap_vals, X_test, feature_names=feature_cols, show=False)
    axes[1].set_title("SHAP — Feature Impact Distribution", fontweight="bold")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def full_evaluation_report(model, X_test, y_test, df_meta=None) -> dict:
    """
    Run the complete evaluation suite and print a summary.
    Returns a dict with all metrics and the fairness DataFrame.
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = compute_metrics(y_test, y_pred, y_prob)
    print("=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=["Not At Risk", "High Risk"]))
    print(f"AUC-ROC: {metrics.get('auc', 'N/A'):.4f}")

    fairness_df = pd.DataFrame()
    if df_meta is not None:
        fairness_df = fairness_analysis(
            X_test, y_test, y_pred, df_meta,
            group_cols=["level", "rural_group"]
        )
        print("\n=== Fairness Analysis (Equalized Odds) ===")
        print(fairness_df.to_string(index=False))

    return {"metrics": metrics, "fairness": fairness_df}
