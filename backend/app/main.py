from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import routers
from app.routes import patient, trial, match

# Database
from app.db.database import engine
from app.db.models import Base

app = FastAPI(
    title="AI-powered Clinical Trial Matching System",
    version="1.0.0"
)

# -----------------------------
# ✅ CORS Middleware (FIXED)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in prod if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ✅ Startup Event (SAFE VERSION)
# -----------------------------
@app.on_event("startup")
def startup_event():
    print("🚀 App is starting up...")
    print("📋 Creating database tables (if they don't exist)...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready.")
    except Exception as e:
        print("❌ Database initialization failed:")
        print(e)

# -----------------------------
# ✅ Include Routers
# -----------------------------
app.include_router(patient.router, prefix="/patients", tags=["Patients"])
app.include_router(trial.router, prefix="/trials", tags=["Trials"])
app.include_router(match.router, prefix="/match", tags=["Matching"])

# -----------------------------
# ✅ Health Check Route
# -----------------------------
@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "🚀 Clinical Trial Matching API is running"
    }

# -----------------------------
# ✅ Optional: Local Run Support
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
