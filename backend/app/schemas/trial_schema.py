from pydantic import BaseModel

from typing import Optional

class TrialCreate(BaseModel):
    nct_id: str
    title: Optional[str] = ""
    condition: str
    text: str
    eligibility: Optional[str] = ""

class TrialResponse(BaseModel):
    id: int
    nct_id: str
    title: Optional[str] = ""
    condition: str
    text: str
    eligibility: Optional[str] = ""
    score: float = 0.0
    confidence: str = "Low"
    explanation: str = ""

    class Config:
        from_attributes = True