# Rural Teacher Attrition Early Warning System (EWS)

## BSc Software Engineering Capstone Project – Machine Learning Track

**Author:** Florence Kabeya  
**Institution:** African Leadership University  
**Supervisor:** Elvira Khwatenge  

---

# 1. Project Overview

The Rural Teacher Attrition Early Warning System (EWS) is a machine learning-based decision support system designed to identify provinces in Zambia that are at increased risk of teacher shortages.

The system uses historical education statistics from Zambia's Ministry of Education Education Statistics Bulletins and applies machine learning techniques to predict teacher attrition risk.

The system provides:

- Province-level teacher attrition risk predictions
- XGBoost machine learning classification
- SHAP-based model explanations
- Interactive Streamlit dashboard
- FastAPI REST backend
- JWT authentication
- Role-based access control
- Dataset upload functionality
- Historical teacher trend analysis


The system is designed as a **decision-support tool** and does not replace education policy experts or automated decision-making processes.

---

# 2. System Architecture

The application consists of three main components:
                User
                  |
                  |
          Streamlit Dashboard
              (Frontend)
                  |
                  |
          FastAPI REST API
              (Backend)
                  |
    ------------------------------
    |                            |
SQLite Database              ML Pipeline
Users                       XGBoost Model
Predictions                 SHAP Explainer
Province Data


---

# 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.11 |
| Frontend | Streamlit |
| Backend API | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Machine Learning | XGBoost |
| Data Processing | Pandas, NumPy |
| Explainability | SHAP |
| Visualisation | Plotly |
| API Server | Uvicorn |


---

# 4. Repository Structure
│
├── app/
│ ├── core/ # Configuration and security
│ ├── database/ # Database connection and sessions
│ ├── models/ # SQLAlchemy database models
│ ├── schemas/ # Pydantic schemas
│ ├── routers/ # API endpoints
│ ├── services/ # Business logic
│ ├── ml_models/ # Trained ML models and explainers
│ ├── scripts/ # Utility scripts
│ └── main.py # FastAPI application entry point
│
├── streamlit_app/
│ ├── views/ # Dashboard pages
│ ├── components/ # Reusable UI components
│ ├── api_client.py # Backend communication
│ ├── styles.py # Dashboard styling
│ └── app.py # Streamlit entry point
│
├── data/
│ ├── raw/ # Original datasets
│ └── processed/ # Feature engineered datasets
│
├── database/
│ └── ews.db # Pre-populated SQLite database
│
├── requirements.txt
├── README.md
└── .gitignore


---

# 5. Prerequisites

Before running the project, install:

- Python 3.11+
- Git

Check installation:

```bash
python --version

git --version

git clone https://github.com/Flo-renc/rural-teacher-ews-zambia.git

cd rural-teacher-ews-zambia

python -m venv venv

venv\Scripts\activate

Linux / macOS
python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

SECRET_KEY=your_secret_key_here

ACCESS_TOKEN_EXPIRE_MINUTES=60

DATABASE_URL=sqlite:///./ews.db

The repository includes a pre-populated SQLite database.

The database contains:

Users table

Stores:

User ID
Username
Password hash
Role
Province access
Account creation date
Province Data table

Stores:

Province
Year
Teacher numbers
Student enrolment
Primary schools
Rural schools
Urban schools
Predictions table

Stores:

Province
Prediction year
Risk score
Risk classification
Model version
SHAP explanations

The database does not store personal teacher information.


# Running the Backend API
uvicorn app.main:app --reload

Application startup complete

http://localhost:8000

API Documentation

FastAPI automatically generates documentation.

Open:

http://localhost:8000/docs

Available endpoints include:

Method	Endpoint	Description
POST	/api/v1/auth/login	User authentication
GET	/api/v1/auth/me	Current user
GET	/api/v1/health	System status
GET	/api/v1/predictions	View predictions
POST	/api/v1/predictions/run-all	Run national predictions
POST	/api/v1/predictions/run/{province}	Run province prediction
GET	/api/v1/predictions/{province}/shap	SHAP explanation
POST	/api/v1/upload/bulletin-csv	Upload education dataset
13. Running Streamlit Dashboard

Open another terminal.

Activate environment:

Windows:

venv\Scripts\activate

Navigate:

cd streamlit_app

Run:

streamlit run app.py

Dashboard:

http://localhost:8501

14. Authentication

The dashboard uses JWT authentication.

Users are created through the backend administration process.

Public registration is intentionally disabled to prevent unauthorized access.

Available roles:

Data Administrator

Permissions:

Upload datasets
Run predictions
View model explanations
District Officer

Permissions:

View prediction results
Analyse province risk
Viewer

Permissions:

View dashboard information
15. Demo Accounts

The database contains pre-created demonstration users.

Example:

Username	Role
admin	Data Administrator
district_officer	District Officer
viewer	Viewer

Passwords are managed locally through the database.

16. Machine Learning Pipeline

The machine learning workflow consists of:

Data extraction from Ministry of Education bulletins
Data cleaning and preprocessing
Feature engineering

Generated features include:

Teacher growth rate
Enrolment growth rate
Recruitment gap
Teacher per school ratio
Learners per school ratio
Rural school percentage
PTR trends
Attrition proxy rate
Model training

The final model:

XGBoost Binary Classifier

Evaluation:

Leave-One-Province-Out Cross Validation
AUC
Recall
F1 Score
Explainability

SHAP is used to explain:

Which features increased risk
Which features reduced risk
Why a province received a prediction
17. Data Sources

The project uses publicly available aggregate education data.

Sources:

Zambia Ministry of Education Education Statistics Bulletins
UNESCO Institute for Statistics

No personally identifiable information is used.

18. Uploading New Data

Only Data Administrators can upload datasets.

Expected CSV columns:

province
year
teacher_count_primary
student_enrolment_primary
primary_schools
rural_schools
urban_schools
ptr_primary

Example:

Central,2025,13294,596557,1398,1124,296

After uploading:

Dataset is stored in the database
Previous provincial data is updated
New predictions can be generated
19. Limitations

Current limitations:

Predictions are generated at provincial level
Teacher attrition is estimated using proxy indicators
Historical data may contain existing structural inequalities
Model predictions require interpretation by education experts

The system should support decision-making rather than replace human judgement.

20. Future Improvements

Future versions may include:

School-level prediction using EMIS data
PostgreSQL deployment
Automated model retraining
Cloud deployment
Additional fairness monitoring
Expanded role management
21. Running Tests

Run:

pytest
22. Author

Florence Kabeya

Bachelor of Software Engineering

African Leadership University

Supervisor:

Elvira Khwatenge

African Leadership University




