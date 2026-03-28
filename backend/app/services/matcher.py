from sqlalchemy.orm import Session
from app.db.crud import get_patient, get_all_trials
from app.services.preprocessing import extract_clinical_features
from app.services.embedding import generate_embeddings
from app.services.explainer import generate_dynamic_explanation, get_confidence_level
from app.core.constants import SCORE_DECAY_FACTOR, CONDITION_MATCH_BOOST

def match_patient_to_trials(patient_id: int, db: Session):
    patient = get_patient(db, patient_id)
    if not patient:
        return []

    trials = get_all_trials(db)
    if not trials:
        return []

    patient_conditions_list = [c.strip() for c in patient.conditions.split(",")]
    patient_history_words = set(patient.history.lower().split()) if patient.history else set()
    
    matches_unsorted = []
    
    for trial in trials:
        trial_condition_lower = trial.condition.lower() if trial.condition else ""
        trial_text_lower = trial.text.lower() if trial.text else ""
        
        boost = 0.0
        matched_terms = []
        
        for cond in patient_conditions_list:
            if cond.lower() in trial_condition_lower or cond.lower() in trial_text_lower:
                boost += CONDITION_MATCH_BOOST
                matched_terms.append(cond)
                
        # Quick text overlap for baseline score
        trial_words = set(trial_text_lower.split())
        overlap = len(patient_history_words.intersection(trial_words))
        
        # Compute final score without PyTorch ML models
        raw_score = 0.3 + (min(overlap, 20) * 0.01) # Baseline 0.3 -> 0.5
        final_score = min(0.99, raw_score + boost)
        
        confidence = get_confidence_level(final_score)
        explanation = generate_dynamic_explanation(final_score, matched_terms)

        matches_unsorted.append({
            "trial_id": trial.id,
            "nct_id": trial.nct_id,
            "title": trial.title or "Untitled Study",
            "condition": trial.condition,
            "text": trial.text,
            "eligibility": trial.eligibility,
            "score": final_score,
            "confidence": confidence,
            "explanation": explanation,
            "eligible": True 
        })
        
    # Return top 5 matches
    matches_unsorted.sort(key=lambda x: x["score"], reverse=True)
    return matches_unsorted[:5]
