from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.matcher import match_patient_to_trials

router = APIRouter()

@router.get("/match/{patient_id}")
def match_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Find matching trials for a specific patient.
    """
    matches = match_patient_to_trials(patient_id, db)
    return {"patient_id": patient_id, "matches": matches}
