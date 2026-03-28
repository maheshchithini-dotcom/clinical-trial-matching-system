from fastapi import FastAPI
from app.routes import patient, trial, match
from app.db.database import engine
from app.db.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI-powered Clinical Trial Matching System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patient.router, tags=["Patients"])
app.include_router(trial.router, tags=["Trials"])
app.include_router(match.router, tags=["Matching"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-powered Clinical Trial Matching System API"}
