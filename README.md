# Teacher Attrition Early Warning System — Chongwe District, Zambia

**BSc. Software Engineering Capstone Project**
African Leadership University | Florence Kabeya | Supervisor: Elvira Khwatenge | 2026

---

## What This Project Does

This project builds a machine learning-based decision-support prototype that predicts teacher attrition risk for schools in Chongwe District, Lusaka Province, Zambia. It converts existing Ministry of Education administrative data into forward-looking risk scores, so that district education officers can identify which schools are likely to lose teachers before vacancies occur — rather than reacting after the fact.

The system is not an automated decision-maker. It surfaces risk signals and plain-language SHAP explanations to support human judgement.

---

## Project Structure

```
teacher-attrition-ews/
│
├── data/
│   ├── raw/                        # Original downloaded datasets (do not edit)
│   │   ├── moe_bulletin_2022.csv
│   │   ├── unesco_uis_zambia.csv
│   │   └── worldbank_edstats.csv
│   ├── processed/                  # Cleaned and feature-engineered data
│   │   ├── chongwe_clean.csv
│   │   └── chongwe_features.csv
│   └── provenance.md               # Source, access date, hash, and licence for each dataset
│
├── notebooks/
│   ├── 01_eda.ipynb                # Exploratory data analysis and visualisations
│   ├── 02_feature_engineering.ipynb
│   ├── 03_label_construction.ipynb # Proxy attrition label (15% headcount threshold)
│   ├── 04_model_training.ipynb     # Logistic regression, XGBoost, Random Forest
│   ├── 05_evaluation.ipynb         # Recall, F1, AUC-ROC, fairness checks
│   └── 06_shap_analysis.ipynb      # SHAP explainability and summary plots
│
├── src/
│   ├── api/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── predict.py          # POST /predict and GET /predict endpoints
│   │   │   ├── explain.py          # GET /explain — SHAP values for a school
│   │   │   └── upload.py           # POST /upload — new MoE Bulletin CSV
│   │   ├── schemas.py              # Pydantic request/response models
│   │   └── db.py                   # MySQL connection and session management
│   │
│   ├── ml/
│   │   ├── pipeline.py             # Full sklearn Pipeline (cleaning + model)
│   │   ├── train.py                # Training script — run from CLI
│   │   ├── evaluate.py             # Evaluation metrics and fairness checks
│   │   ├── shap_explain.py         # SHAP TreeExplainer wrapper
│   │   └── features.py             # Feature engineering functions
│   │
│   └── dashboard/
│       └── app.py                  # Streamlit dashboard entry point
│
├── models/
│   └── .gitkeep                    # Serialised model files stored here (gitignored)
│
├── mlruns/
│   └── .gitkeep                    # MLflow experiment tracking (gitignored)
│
├── sql/
│   └── schema.sql                  # MySQL schema — CREATE TABLE statements
│
├── tests/
│   ├── test_pipeline.py            # Unit tests for feature engineering and labelling
│   ├── test_api.py                 # API endpoint tests (FastAPI TestClient)
│   └── test_shap.py                # SHAP output shape and value range checks
│
├── outputs/
│   ├── figures/                    # EDA plots, SHAP summary plots, confusion matrices
│   └── reports/                    # Evaluation summary CSVs and PDF district report
│
├── .env.example                    # Template for environment variables (no secrets)
├── .gitignore
├── requirements.txt                # Python dependencies with pinned versions
├── Dockerfile                      # Container for FastAPI backend + MySQL
├── docker-compose.yml              # Spins up API, database, and dashboard together
└── README.md
```

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/teacher-attrition-ews.git
cd teacher-attrition-ews
```

### 2. Set up the environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your MySQL credentials
```

### 4. Set up the database

```bash
mysql -u root -p < sql/schema.sql
```

### 5. Run the notebooks in order

Open in Google Colab or Jupyter. Run notebooks `01` through `06` in sequence. The trained model will be saved to `models/`.

### 6. Start the API

```bash
uvicorn src.api.main:app --reload
# Swagger UI available at http://localhost:8000/docs
```

### 7. Launch the dashboard

```bash
streamlit run src/dashboard/app.py
```

### 8. Or run everything with Docker

```bash
docker-compose up --build
```

---

## Data Sources

| Dataset | Source | Role | Licence |
|---|---|---|---|
| MoE Education Statistics Bulletin 2022 | Government of Zambia | Primary | Public, non-commercial research permitted |
| UNESCO UIS Zambia Indicators 2010-2022 | UNESCO Institute for Statistics | Supplementary | Open data, attribution required |
| World Bank EdStats | World Bank | Contextual benchmarks | Open data, CC BY 4.0 |

Raw data files are included in `data/raw/`. See `data/provenance.md` for access dates, file hashes, and full licence details.

---

## ML Pipeline Summary

1. **Features** -- PTR deviation from provincial mean, qualification gap ratio, rural isolation flag, year-on-year teacher count delta, enrolment growth rate, province fixed effects
2. **Label** -- Binary: district loses more than 15% of teacher headcount between consecutive bulletin years = high risk (1). Sensitivity checks at 10% and 20% thresholds are documented in `notebooks/03_label_construction.ipynb`
3. **Models benchmarked** -- Logistic Regression (baseline), XGBoost, Random Forest
4. **Evaluation metrics** -- Recall (primary), F1-score, AUC-ROC, Precision
5. **Explainability** -- SHAP TreeExplainer applied to the best-performing model
6. **Fairness check** -- Disaggregated by school type and rural/urban classification

All experiment runs are tracked with MLflow. See `mlruns/` after training.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/predict?school_code=X` | Returns risk score, risk label, and SHAP values for one school |
| POST | `/predict/batch` | Batch predictions for all Chongwe schools |
| GET | `/explain?school_code=X` | Returns SHAP feature attributions as JSON |
| POST | `/upload` | Upload a new MoE Bulletin CSV to refresh predictions |
| GET | `/health` | API health check |

Full interactive docs at `/docs` (Swagger UI) when the API is running.

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML pipeline | Python, scikit-learn, XGBoost, pandas, NumPy |
| Explainability | SHAP |
| Experiment tracking | MLflow |
| Backend API | FastAPI |
| Database | MySQL |
| Dashboard | Streamlit |
| Visualisation | Plotly, Matplotlib |
| Containerisation | Docker, docker-compose |
| Hosting (planned) | Render / Railway |

---

## Licences and Attribution

All third-party libraries used in this project are open-source:

| Library | Licence |
|---|---|
| scikit-learn | BSD 3-Clause |
| XGBoost | Apache 2.0 |
| FastAPI | MIT |
| Streamlit | Apache 2.0 |
| SHAP | MIT |
| MLflow | Apache 2.0 |
| pandas | BSD 3-Clause |
| NumPy | BSD 3-Clause |

Full citations for all libraries, datasets, and academic references are provided in the project report.

---

## Ethical Considerations

- All datasets are aggregate administrative statistics. No personally identifiable information about individual teachers or students is used at any point.
- The system is a decision-support tool. It does not make employment decisions about individual teachers.
- Model outputs must be interpreted by a district officer with local knowledge, not acted on automatically.
- Fairness evaluation is included to check for systematic over- or under-flagging of any school subgroup.
- See the project ethics form for full documentation.

---

## Project Status

| Task | Status |
|---|---|
| Proposal completed and revised | Done |
| Data acquisition | Done |
| Data cleaning and feature engineering | In progress |
| Proxy label construction | Not started |
| Model training and benchmarking | Not started |
| SHAP analysis | Not started |
| FastAPI backend | Not started |
| Streamlit dashboard | Not started |
| Evaluation and report | Not started |

---

## Contact

**Student:** Florence Kabeya — f.kabeya@alustudent.com
**Supervisor:** Elvira Khwatenge — e.khwatenge@alueducation.com
African Leadership University | BSc. Software Engineering | 2026