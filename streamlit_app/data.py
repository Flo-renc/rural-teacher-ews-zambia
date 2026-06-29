import pandas as pd
import numpy as np

np.random.seed(42)

PROVINCES = [
    "Lusaka", "Copperbelt", "Central", "Eastern",
    "Northern", "North-Western", "Southern", "Western",
    "Luapula", "Muchinga"
]

DISTRICTS = {
    "Lusaka":        ["Chongwe", "Kafue", "Luangwa", "Lusaka", "Chilanga"],
    "Copperbelt":    ["Kitwe", "Ndola", "Chingola", "Mufulira", "Kalulushi"],
    "Central":       ["Kabwe", "Mkushi", "Serenje", "Chibombo", "Mumbwa"],
    "Eastern":       ["Chipata", "Petauke", "Lundazi", "Katete", "Mambwe"],
    "Northern":      ["Kasama", "Mpika", "Chinsali", "Mbala", "Luwingu"],
    "North-Western": ["Solwezi", "Mwinilunga", "Kasempa", "Kabompo", "Chavuma"],
    "Southern":      ["Livingstone", "Choma", "Monze", "Mazabuka", "Namwala"],
    "Western":       ["Mongu", "Kaoma", "Senanga", "Kalabo", "Lukulu"],
    "Luapula":       ["Mansa", "Samfya", "Nchelenge", "Kawambwa", "Milenge"],
    "Muchinga":      ["Chinsali", "Isoka", "Nakonde", "Shiwang'andu", "Mafinga"],
}

SCHOOL_TYPES = ["Primary", "Secondary"]
RISK_LEVELS  = ["High", "Medium", "Low"]

def _risk_weight(province):
    """Rural provinces skew higher risk."""
    rural = {"Western", "Luapula", "Muchinga", "North-Western", "Northern"}
    if province in rural:
        return [0.45, 0.35, 0.20]
    return [0.15, 0.35, 0.50]


def generate_schools(n=120):
    rows = []
    for i in range(n):
        province = np.random.choice(PROVINCES)
        district = np.random.choice(DISTRICTS[province])
        risk     = np.random.choice(RISK_LEVELS, p=_risk_weight(province))
        baseline = np.random.randint(8, 40)
        attrition_pct = (
            np.random.uniform(20, 45) if risk == "High"
            else np.random.uniform(8, 20) if risk == "Medium"
            else np.random.uniform(0, 8)
        )
        rows.append({
            "school_id":       f"ZMB-{1000 + i}",
            "school_name":     f"{district} {'Primary' if i % 2 == 0 else 'Secondary'} School {i+1}",
            "province":        province,
            "district":        district,
            "school_type":     "Primary" if i % 2 == 0 else "Secondary",
            "risk_level":      risk,
            "risk_score":      round(
                np.random.uniform(0.70, 0.95) if risk == "High"
                else np.random.uniform(0.40, 0.70) if risk == "Medium"
                else np.random.uniform(0.05, 0.40), 3
            ),
            "teachers_2022":   baseline,
            "teachers_2023":   max(1, int(baseline * (1 - attrition_pct / 100))),
            "attrition_pct":   round(attrition_pct, 1),
            "pupil_teacher_ratio": round(np.random.uniform(30, 80), 1),
            "rural":           province in {"Western", "Luapula", "Muchinga", "North-Western", "Northern"},
            "latitude":        np.random.uniform(-17.5, -8.0),
            "longitude":       np.random.uniform(21.5, 33.5),
        })
    return pd.DataFrame(rows)


def generate_trend_data():
    years = list(range(2009, 2026))
    rows  = []
    for province in PROVINCES:
        base = np.random.randint(800, 3500)
        for year in years:
            trend    = -0.015 if province in {"Western", "Luapula", "Muchinga"} else 0.012
            noise    = np.random.normal(0, 0.03)
            teachers = int(base * (1 + trend + noise) ** (year - 2009))
            rows.append({
                "year":     year,
                "province": province,
                "teachers": max(100, teachers),
            })
    return pd.DataFrame(rows)


def get_national_summary(df_schools):
    total  = len(df_schools)
    high   = (df_schools["risk_level"] == "High").sum()
    medium = (df_schools["risk_level"] == "Medium").sum()
    low    = (df_schools["risk_level"] == "Low").sum()
    avg_attrition = df_schools["attrition_pct"].mean()
    return {
        "total_schools":   total,
        "high_risk":       high,
        "medium_risk":     medium,
        "low_risk":        low,
        "avg_attrition":   round(avg_attrition, 1),
        "high_pct":        round(high / total * 100, 1),
        "provinces_flagged": df_schools[df_schools["risk_level"] == "High"]["province"].nunique(),
    }


def shap_feature_importance():
    features = [
        "Pupil-Teacher Ratio",
        "Prior Year Attrition",
        "Remoteness Index",
        "School Type (Secondary)",
        "Province (Western)",
        "Housing Availability",
        "Years Without Promotion",
        "Transfer Request Rate",
        "Salary Delay Index",
        "District Budget Allocation",
    ]
    mean_shap = np.array([0.38, 0.29, 0.22, 0.17, 0.14, 0.11, 0.09, 0.07, 0.05, 0.03])
    return pd.DataFrame({"feature": features, "mean_shap": mean_shap})