from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.schemas.patient_schema import PatientCreate
from app.db.database import get_db
from app.db.crud import create_patient, get_all_patients
from app.services.document_service import extract_text_from_file

router = APIRouter()

@router.get("/")
def list_patients(db: Session = Depends(get_db)):
    return get_all_patients(db)

@router.post("/")
def add_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient = create_patient(db, data)
    return {
        "message": "Patient created successfully",
        "patient_id": patient.id
    }

@router.post("/parse_document")
async def parse_patient_document(file: UploadFile = File(...)):
    """
    Extract text from an uploaded patient report (PDF, DOCX, TXT).
    """
    try:
        content = await file.read()
        text = extract_text_from_file(content, file.filename)
        return {"text": text}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        print("❌ Error parsing document:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error parsing document: {str(e)}")