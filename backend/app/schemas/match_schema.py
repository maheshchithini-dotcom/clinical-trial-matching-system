
from pydantic import BaseModel


class EligibilityMatch(BaseModel):
    age: bool
    gender: bool
    condition: bool


class MatchResponse(BaseModel):
    trial_id: int
    score: float
    explanation: str
    confidence: str
    eligibility_match: EligibilityMatch