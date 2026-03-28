from pydantic import BaseModel

class TrialCreate(BaseModel):
    nct_id: str
    title: str = ""
    condition: str
    text: str
    eligibility: str = ""

class TrialResponse(BaseModel):
    id: int
    nct_id: str
    title: str = ""
    condition: str
    text: str
    eligibility: str = ""
    score: float = 0.0
    confidence: str = "Low"
    explanation: str = ""

    class Config:
        from_attributes = True