from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.trial_schema import TrialCreate, TrialResponse
from app.db.database import get_db
from app.db.crud import create_trial
from app.services.ingestion import fetch_trials_from_api

from app.db.crud import create_trial, get_all_trials

router = APIRouter()

@router.get("/", response_model=list[TrialResponse])
def list_trials(db: Session = Depends(get_db)):
    return get_all_trials(db)

@router.post("/fetch_trials")
def fetch_trials(condition: str, db: Session = Depends(get_db)):
    """
    Fetch clinical trials from ClinicalTrials.gov API for a given condition.
    """
    trials_added = fetch_trials_from_api(db, condition)
    return {"message": f"Successfully fetched {trials_added} trials for {condition}"}

@router.post("/", response_model=TrialResponse)
def add_trial(trial: TrialCreate, db: Session = Depends(get_db)):
    return create_trial(db, trial.dict())
