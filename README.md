#  Rural Teacher Attrition Early Warning System (EWS)

> **BSc Software Engineering Capstone — ML Track**
> African Leadership University | Florence Kabeya 

---

## Description

The Rural Teacher Attrition Early Warning System is a machine-learning decision-support prototype that predicts which provinces and school clusters in Zambia are at elevated risk of losing teachers. It is built for district education officers in Chongwe District, Lusaka Province, and trained on the Ministry of Education Education Statistics Bulletin 2022 (all 10 provinces).

The system flags high-risk schools before vacancies become critical, giving officers enough lead time to deploy retention interventions such as hardship allowances, housing support, or professional development placements.

**Core ML model:** XGBoost binary classifier (primary metric: Recall), benchmarked against Logistic Regression, Random Forest, Decision Tree, and SVM. Every prediction includes SHAP feature attributions translated into plain language for non-technical users.

---

## GitHub Repository

https://github.com/Flo-renc/rural-teacher-ews-zambia.git

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Framework | XGBoost 2.0, scikit-learn 1.4, SHAP 0.45 |
| Experiment Tracking | MLflow 2.12 |
| Backend API | FastAPI 0.111, Uvicorn |
| Database | MySQL 8.0 (SQLite for local dev) |
| Dashboard | Streamlit 1.34 |
| Data Processing | pandas 2.2, NumPy 1.26 |
| Deployment | Render (free tier) |
| Language | Python 3.11 |

---

## Project Structure

```
rural-teacher-ews-zambia/
├── README.md
├── .env                        # local environment variables (not committed)
├── .gitignore
├── requirements.txt
├── setup.sh                    # one-command local setup
│
├── data/
│   ├── raw/                    # MoE Bulletin 2022 CSVs (not committed)
│   ├── processed/              # cleaned, feature-engineered exports
│   └── provenance_log.md       # dataset source, date, hash, licence
│
├── notebooks/
│   └── 01_eda_baseline.ipynb   # EDA → feature engineering → model training
│
├── src/
│   ├── data/
│   │   ├── ingest.py           # loads raw CSVs, validates schema
│   │   ├── clean.py            # missing values, type casting, outlier checks
│   │   └── db.py               # SQLAlchemy engine + session factory
│   ├── features/
│   │   └── engineer.py         # all 8 engineered features
│   ├── models/
│   │   ├── db_models.py        # ORM table definitions
│   │   ├── train.py            # training pipeline + MLflow logging
│   │   ├── evaluate.py         # metrics + fairness evaluation
│   │   └── predict.py          # inference service + SHAP explanations
│   └── api/
│       ├── main.py             # FastAPI app entry point
│       ├── schemas/
│       │   └── schemas.py      # Pydantic request/response models
│       └── routers/
│           ├── predictions.py  # POST /predict, POST /predict/batch
│           ├── schools.py      # CRUD /schools
│           ├── data_upload.py  # POST /upload (CSV)
│           └── health.py       # GET /health
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard
│
├── database/
│   └── schema.sql              # MySQL DDL (also auto-created by ORM)
│
├── docs/
│   └── api_mockup.md           # Swagger UI / Postman endpoint reference
│
├── tests/
│   └── test_api.py             # pytest test suite
│
├── models/                     # serialised .pkl artefacts (not committed)
└── mlruns/                     # MLflow experiment runs (not committed)
```

---

## Environment Setup

### 1. Clone the repository

```bash
git clone https://github.com/florencekabeya/rural-teacher-ews-zambia.git
cd rural-teacher-ews-zambia
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env — for local dev you can leave DB_PASSWORD empty (uses SQLite)
```

### 5. Train the model

Open and run `notebooks/01_eda_baseline.ipynb` top to bottom. This produces:
- `models/xgboost_attrition_model.pkl`
- `models/feature_scaler.pkl`
- `models/feature_cols.json`

Or use the training script directly:

```bash
python src/models/train.py
```

### 6. Start the API

```bash
uvicorn src.api.main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 7. Start the dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard available at: `http://localhost:8501`

### Quick start (all steps at once)

```bash
chmod +x setup.sh && ./setup.sh
```

---

## MySQL Setup (production)

If you want to use MySQL instead of SQLite:

```bash
# 1. Create the database
mysql -u root -p < database/schema.sql

# 2. Update .env with your credentials
DB_HOST=localhost
DB_PORT=3306
DB_NAME=teacher_ews
DB_USER=ews_user
DB_PASSWORD=your_password
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | API + model + DB status |
| POST | `/api/v1/predict` | Single school risk prediction |
| POST | `/api/v1/predict/batch` | Batch prediction (up to 200 schools) |
| GET | `/api/v1/predict/history/{school_code}` | Prediction history |
| GET | `/api/v1/schools` | List all registered schools |
| POST | `/api/v1/schools` | Register a school |
| POST | `/api/v1/upload` | Upload MoE Bulletin CSV |

Full request/response schemas: see `docs/api_mockup.md` or `http://localhost:8000/docs`

---

## Designs

- **Figma mockup:** [link to be added before submission]
- **API UI screenshots:** see `docs/api_mockup.md`
- **System architecture diagram:** see `docs/api_mockup.md`

---

## Deployment Plan

### Platform: Render (free tier)

**API (FastAPI)**
1. Push repo to GitHub
2. Create a new Render Web Service → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env` in the Render dashboard

**Dashboard (Streamlit)**
1. Create a second Render Web Service
2. Start command: `streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0`
3. Set `API_BASE_URL` to your deployed FastAPI URL

**Database**
1. Create a Render MySQL instance (or use PlanetScale free tier)
2. Copy the connection string into your Render environment variables

**Model artefacts**
- Upload `models/*.pkl` and `models/*.json` to Render persistent disk or a public S3 bucket
- Set `MODEL_DIR` environment variable to the mounted path

---

## Dataset Sources

| Dataset | Source | Year | Licence |
|---|---|---|---|
| MoE Education Statistics Bulletin | Zambia Ministry of Education | 2022 | Public |
| UNESCO UIS Zambia Time-Series | UNESCO Institute for Statistics | 2010–2022 | CC-BY |
| Zambia LCMS | Central Statistical Office | 2022 | Public |

See `data/provenance_log.md` for full provenance details.

---

## Limitations

- The attrition risk label is a proxy derived from year-on-year teacher headcount changes (>15% decline = high risk). It does not directly record individual teacher departures.
- The model is trained on province-level aggregates from the 2022 Bulletin. School-level EMIS data from the MoE would significantly improve precision.
- This is a decision-support prototype, not a production system. Predictions should be used alongside local contextual knowledge.
- Results are not intended to inform employment decisions about individual teachers.

---

## Author

**Florence Kabeya** — f.kabeya@alustudent.com

## Supervisor
**Elvira Khwatenge** — ekhwatenge@alueducation.com

African Leadership University | BSc Software Engineering | Capstone 2026