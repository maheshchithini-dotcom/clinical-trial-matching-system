import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

_db_url = os.getenv("DATABASE_URL", "")
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-powered Clinical Trial Matching System"
    
    # Database
    DATABASE_URL: str = _db_url
    # AI Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CLINICAL_NER_MODEL: str = "dmis-lab/biobert-v1.1"
    
    # Matching Engine Settings
    MAX_TRIALS_TO_SYNC: int = 100
    DEFAULT_MATCH_LIMIT: int = 10
    
    class Config:
        case_sensitive = True

settings = Settings()
