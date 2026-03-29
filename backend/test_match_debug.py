import sys
import os
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.matcher import match_patient_to_trials
import traceback

def test_debug():
    db = SessionLocal()
    print("🚀 Starting clinical matching debug for Patient ID 3...")
    try:
        results = match_patient_to_trials(3, db)
        print("\n✅ MATCH RESULTS:")
        for r in results:
            print(f"- {r['title']} | Score: {r['score']} | Expl: {r['explanation'][:50]}...")
    except Exception as e:
        print("\n❌ MATCH FAILED:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_debug()
