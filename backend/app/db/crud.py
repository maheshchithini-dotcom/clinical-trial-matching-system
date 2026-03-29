
from sqlalchemy.orm import Session
from app.db.models import Patient, Trial


# ------------------ PATIENT ------------------

def create_patient(db: Session, data):
    patient = Patient(
        name=data.name,
        age=data.age,
        gender=data.gender,
        conditions=",".join(data.conditions),
        history=data.history
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_all_patients(db: Session):
    return db.query(Patient).all()


def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()


# ------------------ TRIAL ------------------

def create_trial(db: Session, trial_data):
    trial = Trial(**trial_data)
    db.add(trial)
    db.commit()
    db.refresh(trial)
    return trial


def get_all_trials(db: Session):
    return db.query(Trial).all()


def get_trial_by_id(db: Session, trial_id: int):
    return db.query(Trial).filter(Trial.id == trial_id).first()