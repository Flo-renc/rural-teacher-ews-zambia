"""
Teacher Attrition Early Warning System — FastAPI Backend
Authors: Florence Kabeya & Elvira Khwatenge | African Leadership University
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
 
from app.routers import predictions, schools, data_upload, health
from app.database.connection import create_tables
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before the app starts accepting requests."""
    logger.info("Starting EWS API — creating database tables if needed...")
    create_tables()
    logger.info("Database ready.")
    yield
    logger.info("EWS API shutting down.")
 
 
app = FastAPI(
    title="Teacher Attrition Early Warning System API",
    description=(
        "ML-based decision support prototype for predicting teacher attrition risk "
        "in Zambian schools. Primary focus: Chongwe District, Lusaka Province. "
        "Built for the 2024–2029 MoE Education Sector Partnership Compact."
    ),
    version="1.0.0",
    contact={
        "name": "Florence Kabeya & Elvira Khwatenge",
        "email": "florence.kabeya@alustudent.com",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
)
 
# CORS — allow Streamlit dashboard and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(schools.router, prefix="/api/v1", tags=["Schools"])
app.include_router(data_upload.router, prefix="/api/v1", tags=["Data Upload"])
 
 
@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({
        "service": "Teacher Attrition EWS API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    })
 