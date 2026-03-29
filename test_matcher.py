import sys
import traceback
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app.db.database import SessionLocal
from app.services.matcher import match_patient_to_trials

db = SessionLocal()
try:
    print("Testing match_patient_to_trials")
    res = match_patient_to_trials(3, db)
    print("Result:")
    print(res)
except Exception as e:
    print("ERROR CAUGHT:")
    traceback.print_exc()
finally:
    db.close()
