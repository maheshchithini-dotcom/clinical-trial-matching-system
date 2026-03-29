from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.matcher import match_patient_to_trials

router = APIRouter()

@router.get("/{patient_id}")
def match_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Find matching trials for a specific patient.
    """
    try:
        matches = match_patient_to_trials(patient_id, db)
        return {"patient_id": patient_id, "matches": matches}
    except Exception as e:
        import traceback
        print(f"🚨 MATCH ERROR: {e}")
        traceback.print_exc()
        try:
            from app.db.crud import get_all_trials
            trials = get_all_trials(db)[:3]
            fallback = [{"trial_id": t.id, "score": 0.50, "explanation": f"Fallback due to error: {str(e)}"} for t in trials]
        except:
            fallback = [{"trial_id": 1, "score": 0.50, "explanation": f"Fallback due to error: {str(e)}"}]
        return {"patient_id": patient_id, "matches": fallback, "status": "fallback_active", "error": str(e)}
