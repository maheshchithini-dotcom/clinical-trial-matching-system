from sqlalchemy.orm import Session
from app.db.crud import get_patient, get_all_trials
from app.services.preprocessing import extract_clinical_features
from app.services.embedding import generate_embeddings
from app.services.explainer import generate_dynamic_explanation, get_confidence_level
from app.core.constants import SCORE_DECAY_FACTOR, CONDITION_MATCH_BOOST

import re

STOP_WORDS = {"the", "a", "an", "is", "are", "of", "to", "in", "and", "or", "for", "with", "on", "at", "by", "patient", "year", "old", "diagnosed", "history", "has", "been", "was", "this", "that", "study", "clinical", "trial", "treatment"}

def _extract_keywords(text: str):
    if not text:
        return set()
    words = re.findall(r'\b\w+\b', text.lower())
    return set(w for w in words if len(w) > 2 and w not in STOP_WORDS)

def _condition_relevance(patient_conditions, trial_condition, trial_text):
    """
    Returns a relevance score (0.0 to 1.0) indicating how relevant a trial is 
    to the patient's conditions. Uses both substring and word-level matching.
    """
    score = 0.0
    combined = trial_condition + " " + trial_text
    
    for cond in patient_conditions:
        # Exact substring match in condition field (highest relevance)
        if cond in trial_condition:
            score += 1.0
        # Exact substring match in trial text/description
        elif cond in combined:
            score += 0.7
        # Word-level: check if ALL words of the condition appear in trial
        else:
            cond_words = set(cond.split())
            combined_words = set(combined.split())
            if cond_words and cond_words.issubset(combined_words):
                score += 0.5
    return score

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

    # Score ALL trials first
    all_scored = []
    
    for trial in trials:
        trial_condition_lower = trial.condition.lower() if trial.condition else ""
        trial_text_lower = trial.text.lower() if trial.text else ""
        
        # Calculate condition relevance
        relevance = _condition_relevance(patient_conditions_list, trial_condition_lower, trial_text_lower)
        
        trial_keywords = _extract_keywords(trial_text_lower)
        trial_keywords.update(_extract_keywords(trial_condition_lower))
        
        boost = 0.0
        matched_terms = []
        
        for cond in patient_conditions_list:
            cond_words = _extract_keywords(cond)
            if cond in trial_condition_lower:
                boost += CONDITION_MATCH_BOOST * 2.0
                matched_terms.append(cond)
            elif cond in trial_text_lower:
                boost += CONDITION_MATCH_BOOST * 1.5
                matched_terms.append(cond)
            elif cond_words and cond_words.issubset(trial_keywords):
                boost += CONDITION_MATCH_BOOST
                matched_terms.append(cond)
                
        # Jaccard Similarity for context overlap
        intersection = patient_keywords.intersection(trial_keywords)
        union = patient_keywords.union(trial_keywords)
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # Base score from Jaccard overlap (0.3 -> 0.7)
        raw_score = 0.3 + (jaccard * 0.4) 
        final_score = min(0.99, raw_score + boost)
        
        # If exact condition match exists, floor score at 0.85
        if boost >= (CONDITION_MATCH_BOOST * 2.0):
            final_score = max(0.85, final_score)
            
        confidence = get_confidence_level(final_score)
        explanation = generate_dynamic_explanation(final_score, list(set(matched_terms)))

        all_scored.append({
            "trial_id": trial.id,
            "nct_id": trial.nct_id,
            "title": trial.title or "Untitled Study",
            "condition": trial.condition,
            "text": trial.text,
            "eligibility": trial.eligibility,
            "score": final_score,
            "confidence": confidence,
            "explanation": explanation,
            "eligible": True,
            "_relevance": relevance  # internal sorting key
        })
    
    # Prefer condition-relevant trials, then sort by score
    # Split into relevant and fallback
    relevant = [m for m in all_scored if m["_relevance"] > 0]
    
    if relevant:
        relevant.sort(key=lambda x: (x["_relevance"], x["score"]), reverse=True)
        results = relevant[:5]
    else:
        # No exact condition match—return best available with lower scores
        all_scored.sort(key=lambda x: x["score"], reverse=True)
        for m in all_scored:
            m["score"] = min(m["score"], 0.35)  # Cap at 35% since no condition match
            m["confidence"] = "Low"
            m["explanation"] = "No direct condition match found. Showing closest available trials."
        results = all_scored[:5]
    
    # Remove internal key before returning
    for r in results:
        r.pop("_relevance", None)
    
    return results
