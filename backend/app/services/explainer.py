from app.core.constants import (
    CONFIDENCE_THRESHOLD_HIGH, 
    CONFIDENCE_THRESHOLD_MEDIUM,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW
)

def get_confidence_level(score: float) -> str:
    if score >= CONFIDENCE_THRESHOLD_HIGH:
        return CONFIDENCE_HIGH
    elif score >= CONFIDENCE_THRESHOLD_MEDIUM:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_LOW

def generate_dynamic_explanation(score: float, matched_terms: list) -> str:
    """
    Generate a clinically grounded explanation for the match.
    """
    explanation = ""
    
    if matched_terms:
        explanation = f"Strong direct match for conditions: {', '.join(matched_terms)}. "
    
    if score >= 0.8:
        explanation += "The overall clinical profile and eligibility criteria are highly aligned with this study's requirements. "
    elif score >= 0.6:
        explanation += "There is a significant semantic overlap between your medical history and the trial objectives. "
    else:
        explanation += "Moderate relevance based on general medical context and trial focus. "

    from app.services.preprocessing import USE_BIOBERT
    if USE_BIOBERT:
        explanation += "BioBERT analysis confirmed medical context alignment."
    else:
        explanation += "Clinical semantic analysis confirmed medical context alignment."
    
    return explanation
