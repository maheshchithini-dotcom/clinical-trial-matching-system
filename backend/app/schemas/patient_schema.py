from pydantic import BaseModel
from typing import List


# 🔹 Input schema
class PatientCreate(BaseModel):
    age: int
    gender: str
    conditions: List[str]
    history: str


# 🔹 Output schema (response)
class PatientResponse(BaseModel):
    id: int
    age: int
    gender: str
    conditions: List[str]
    history: str

    class Config:
        from_attributes = True