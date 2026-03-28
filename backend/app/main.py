from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes import patient, trial, match
from app.db.database import engine
from app.db.models import Base

app = FastAPI(title="AI-powered Clinical Trial Matching System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in prod if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("🚀 App is starting up...")
    print("📋 Creating database tables (if they don't exist)...")
    try:
        from app.db.database import engine
        from app.db.models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables confirmed.")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")

# Include routers
app.include_router(patient.router, tags=["Patients"])
app.include_router(trial.router, tags=["Trials"])
app.include_router(match.router, tags=["Matching"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-powered Clinical Trial Matching System API"}
