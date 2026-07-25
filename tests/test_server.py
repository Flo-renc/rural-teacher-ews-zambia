import joblib
m = joblib.load("app/ml_models/xgb_v1.0.joblib")
print(type(m))

import shap
explainer = shap.TreeExplainer(m)
print("explainer OK")

