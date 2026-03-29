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
    from sqlalchemy import text
    print("🚀 App is starting up...")
    try:
        # Step 1: Ensure basic tables exist
        Base.metadata.create_all(bind=engine)
        
        # Step 2: Safe Auto-Migration for the 'name' column
        with engine.connect() as connection:
            print("📋 Checking database schema integrity...")
            # For PostgreSQL/SQLite compatibility:
            if "postgresql" in str(engine.url):
                connection.execute(text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS name VARCHAR"))
            else:
                # SQLite doesn't support 'ADD COLUMN IF NOT EXISTS' natively in old versions
                # so we use a safe try/except check or just ignore if it fails
                try:
                    connection.execute(text("ALTER TABLE patients ADD COLUMN name VARCHAR"))
                except:
                    pass
            connection.commit()
        print("✅ Database schema is up to date.")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")

# Include routers
app.include_router(patient.router, prefix="/patient", tags=["Patients"])
app.include_router(trial.router, prefix="/trial", tags=["Trials"])
app.include_router(match.router, prefix="/match", tags=["Matching"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-powered Clinical Trial Matching System API"}
