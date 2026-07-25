"""
Teacher Attrition Early Warning System — FastAPI Backend
Authors: Florence Kabeya| African Leadership University
"""

from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
 
from app.database.connection import create_tables
from app.routers import (
    predictions,
    data_upload,
    health,
    auth,
)

 
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
        "name": "Florence Kabeya",
        "email": "f.kabeya@alustudent.com",
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
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(data_upload.router)
 
 
@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({
        "service": "Teacher Attrition EWS API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    })
 