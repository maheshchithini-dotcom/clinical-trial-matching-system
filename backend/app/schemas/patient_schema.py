from pydantic import BaseModel
from typing import List, Optional


# 🔹 Input schema
class PatientCreate(BaseModel):
    name: str = "Anonymous User"
    age: int
    gender: str
    conditions: List[str]
    history: str


# 🔹 Output schema (response) - returns conditions as a string (comma-separated)
class PatientResponse(BaseModel):
    id: int
    name: Optional[str] = "Anonymous User"
    age: int
    gender: str
    conditions: str  # stored as comma-separated string in DB
    history: Optional[str] = ""

    class Config:
        from_attributes = True