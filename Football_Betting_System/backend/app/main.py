import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

# Import routes
from .betting_routes import router as betting_router
from .prediction_routes import router as prediction_router
from .rating_routes import router as rating_router
from .opta_routes import router as opta_router

# Import models to ensure they're registered
from . import models
from . import models_advanced

# FastAPI app
app = FastAPI(title="Football Betting Platform - Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/betting_db")
engine = create_engine(DATABASE_URL, echo=False)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Include routers
app.include_router(betting_router)
app.include_router(prediction_router)
app.include_router(rating_router)
app.include_router(opta_router)
app.include_router(rating_router)
