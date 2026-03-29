from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes import patient, trial, match
from app.db.database import engine
from app.db.models import Base

app = FastAPI(title="AI-powered Clinical Trial Matching System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://clinical-trial-matching-system-3lws2mrkf.vercel.app",
        "https://clinical-trial-matching-system.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    from sqlalchemy import text
    from app.db.database import engine
    from app.db.models import Base
    
    print("🚀 App is starting up...")
    try:
        # Step 1: Ensure basic tables exist
        Base.metadata.create_all(bind=engine)
        
        # Step 2: Safe Auto-Migration for the 'name' column
        with engine.connect() as connection:
            print("📋 Checking database schema integrity...")
            if "postgresql" in str(engine.url):
                connection.execute(text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS name VARCHAR"))
            else:
                try:
                    connection.execute(text("ALTER TABLE patients ADD COLUMN name VARCHAR"))
                except:
                    pass
            
            # Step 3: FORCE-SYNC Identity for Sarah Lee (Patient ID 3)
            print("👤 Syncing Patient Identities...")
            connection.execute(text("""
                UPDATE patients 
                SET name = 'Sarah Lee', age = 47, gender = 'female' 
                WHERE id = 3
            """))
            connection.commit()
            
        print("✅ Database schema and identities are up to date.")
    except Exception as e:
        print(f"⚠️ Startup sequence warning: {e}")

# Include routers
app.include_router(patient.router, prefix="/patient", tags=["Patients"])
app.include_router(trial.router, prefix="/trial", tags=["Trials"])
app.include_router(match.router, prefix="/match", tags=["Matching"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-powered Clinical Trial Matching System API"}
