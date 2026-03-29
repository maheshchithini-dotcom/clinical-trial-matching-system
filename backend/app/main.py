from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes import patient, trial, match
from app.db.database import engine
from app.db.models import Base

app = FastAPI(title="AI-powered Clinical Trial Matching System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("🚀 App is starting up...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables are ready.")
    except Exception as e:
        print(f"⚠️ Startup warning: {e}")

# Include routers
app.include_router(patient.router, prefix="/patient", tags=["Patients"])
app.include_router(trial.router, prefix="/trial", tags=["Trials"])
app.include_router(match.router, prefix="/match", tags=["Matching"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-powered Clinical Trial Matching System API"}
