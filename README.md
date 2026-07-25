Rural Teacher Attrition Early Warning System (EWS)

BSc Software Engineering Capstone Project – Machine Learning Track
African Leadership University
Author: Florence Kabeya

Overview

The Rural Teacher Attrition Early Warning System (EWS) is a machine learning–powered decision support system that predicts teacher attrition risk across Zambia's provinces. The system enables education stakeholders to identify provinces at elevated risk of teacher shortages and provides interpretable explanations for every prediction using SHAP (SHapley Additive Explanations).

The project combines machine learning, a REST API, and an interactive dashboard to support evidence-based planning and resource allocation.

Key Features
Province-level teacher attrition risk prediction
XGBoost classification model
SHAP explainability for transparent predictions
FastAPI REST API
Interactive Streamlit dashboard
User authentication with JWT
SQLite database for local development
CSV upload for prediction data
Interactive visualisations of teacher trends and provincial risk
Technology Stack
Component	Technology
Language	Python 3.11
Machine Learning	XGBoost, Scikit-learn
Explainability	SHAP
Backend	FastAPI
Database	SQLite (SQLAlchemy ORM)
Frontend	Streamlit
Data Processing	Pandas, NumPy
Authentication	JWT
Visualisation	Plotly
Project Structure
rural-teacher-ews-zambia/
│
├── app/
│   ├── core/
│   ├── database/
│   ├── services/
│   ├── ml_models/
│   ├── routers/
│   ├── schemas/
│   ├── scripts/
│   ├── main.py
│   └── models/
│
├── streamlit_app/
│   ├── views/
│   ├── components/
│   ├── styles.py
│   ├── api_client.py
│   └── app.py
│
├── data/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
Installation
Clone the repository
git clone https://github.com/Flo-renc/rural-teacher-ews-zambia.git

cd rural-teacher-ews-zambia
Create a virtual environment

Windows

python -m venv venv

venv\Scripts\activate

Linux/macOS

python3 -m venv venv

source venv/bin/activate
Install dependencies
pip install -r requirements.txt
Environment Variables

Create a .env file inside the project root.

SECRET_KEY=your_secret_key

ACCESS_TOKEN_EXPIRE_MINUTES=60
Running the API
uvicorn app.main:app --reload

Swagger documentation

http://localhost:8000/docs
Running the Dashboard
cd streamlit_app

streamlit run app.py

Dashboard

http://localhost:8501
Authentication

The application uses JWT authentication.

Available roles include:

Data Administrator
District Officer
Viewer
Main API Endpoints
Method	Endpoint	Description
POST	/api/v1/auth/register	Register user
POST	/api/v1/auth/login	Login
GET	/api/v1/auth/me	Current user
GET	/api/v1/health	API health
GET	/api/v1/predictions	Province predictions
GET	/api/v1/predictions/by-province	Province summary
GET	/api/v1/predictions/national-summary	National summary
POST	/api/v1/predictions/run-all	Generate predictions
POST	/api/v1/predictions/run/{province}	Generate province prediction
GET	/api/v1/predictions/{province}/shap	SHAP explanation
GET	/api/v1/predictions/{province}/trend	Historical trend
POST	/api/v1/data/upload	Upload CSV data
Machine Learning Model

The prediction engine uses an XGBoost binary classification model trained on teacher and education statistics collected from Zambia's Ministry of Education.

Model explanations are generated using SHAP, allowing users to understand which factors most influenced each prediction.

Dataset

The project uses publicly available education statistics from Zambia.

Primary sources include:

Zambia Ministry of Education Education Statistics Bulletins
UNESCO Institute for Statistics
Current Limitations
Predictions are generated at the provincial level rather than individual schools.
The model relies on historical education statistics and should be used as a decision-support tool rather than a replacement for expert judgement.
Teacher attrition is estimated using proxy indicators because comprehensive teacher exit records are not publicly available.
Future Improvements
School-level predictions using EMIS data
PostgreSQL deployment
Automatic model retraining
Time-series forecasting
Role-based administration dashboard
Cloud deployment
Author

Florence Kabeya

Bachelor of Software Engineering

African Leadership University

Supervisor

Elvira Khwatenge

African Leadership University