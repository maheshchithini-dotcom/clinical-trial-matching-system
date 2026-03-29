import json
from app.db.database import SessionLocal
from app.services.matcher import match_patient_to_trials
from app.db.models import Patient

db = SessionLocal()
results = match_patient_to_trials(3, db)
db.close()

with open("test_out_id3.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
