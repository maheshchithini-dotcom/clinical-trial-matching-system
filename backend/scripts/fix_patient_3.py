from app.db.database import SessionLocal
from app.db.models import Patient

def fix_patient():
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.id == 3).first()
        if patient:
            print(f"Updating Patient 3: {patient.name} -> Sarah Lee")
            patient.name = "Sarah Lee"
            patient.age = 47
            patient.gender = "female"
            db.commit()
            print("✅ Patient 3 updated successfully.")
        else:
            print("❌ Patient 3 not found.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_patient()
