from sqlalchemy.orm import Session
from app.db.crud import get_patient, get_all_trials
from app.services.preprocessing import extract_clinical_features
from app.services.embedding import generate_embeddings
from app.services.explainer import generate_dynamic_explanation, get_confidence_level
from app.core.constants import SCORE_DECAY_FACTOR, CONDITION_MATCH_BOOST

import re

STOP_WORDS = {"the", "a", "an", "is", "are", "of", "to", "in", "and", "or", "for", "with", "on", "at", "by", "patient", "year", "old", "diagnosed", "history", "has", "been", "was", "this", "that"}

def _extract_keywords(text: str):
    if not text:
        return set()
    words = re.findall(r'\b\w+\b', text.lower())
    return set(w for w in words if len(w) > 2 and w not in STOP_WORDS)

def match_patient_to_trials(patient_id: int, db: Session):
    patient = get_patient(db, patient_id)
    if not patient:
        return []

    trials = get_all_trials(db)
    if not trials:
        return []

    patient_conditions_list = [c.strip().lower() for c in patient.conditions.split(",")]
    
    patient_keywords = _extract_keywords(patient.history)
    for c in patient_conditions_list:
        patient_keywords.update(_extract_keywords(c))

    matches_unsorted = []
    
    # Strict Condition Filter
    def passes_condition_filter(patient_conditions, trial_condition, trial_text):
        for cond in patient_conditions:
            # Check if condition is directly in the trial condition string or description
            if cond in trial_condition or cond in trial_text:
                return True
        return False
        
    for trial in trials:
        trial_condition_lower = trial.condition.lower() if trial.condition else ""
        trial_text_lower = trial.text.lower() if trial.text else ""
        
        # Skip completely irrelevant trials
        if not passes_condition_filter(patient_conditions_list, trial_condition_lower, trial_text_lower):
            continue
            
        trial_keywords = _extract_keywords(trial_text_lower)
        trial_keywords.update(_extract_keywords(trial_condition_lower))
        
        boost = 0.0
        matched_terms = []
        
        for cond in patient_conditions_list:
            cond_words = _extract_keywords(cond)
            # Exact Substring Match gives max boost
            if cond in trial_condition_lower or cond in trial_text_lower:
                boost += CONDITION_MATCH_BOOST * 2.0
                matched_terms.append(cond)
            # Or subset match gives normal boost
            elif cond_words and cond_words.issubset(trial_keywords):
                boost += CONDITION_MATCH_BOOST
                matched_terms.append(cond)
                
        # Jaccard Similarity for context overlap
        intersection = patient_keywords.intersection(trial_keywords)
        union = patient_keywords.union(trial_keywords)
        
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # Base score purely on textual Jaccard overlap (0.3 -> 0.7)
        raw_score = 0.3 + (jaccard * 0.4) 
        
        final_score = min(0.99, raw_score + boost)
        
        # If perfect exact matches exist, ensure the score floors at 0.85
        if boost >= (CONDITION_MATCH_BOOST * 2.0):
            final_score = max(0.85, final_score)
            
        confidence = get_confidence_level(final_score)
        explanation = generate_dynamic_explanation(final_score, list(set(matched_terms)))

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
        
    matches_unsorted.sort(key=lambda x: x["score"], reverse=True)
    return matches_unsorted[:5]
