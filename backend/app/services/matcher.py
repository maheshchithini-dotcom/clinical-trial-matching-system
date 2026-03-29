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

    # Clean patient conditions (e.g. ['diabetes', 'hypertension'])
    patient_conditions_list = [c.strip().lower() for c in patient.conditions.split(",")]
    
    patient_keywords = _extract_keywords(patient.history)
    for c in patient_conditions_list:
        patient_keywords.update(_extract_keywords(c))

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
        conditions_hit = 0
        
        for cond in patient_conditions_list:
            cond_words = _extract_keywords(cond)
            # Check if this specific condition is mentioned
            hit = False
            if cond in trial_condition_lower:
                boost += CONDITION_MATCH_BOOST * 2.0
                matched_terms.append(cond)
                hit = True
            elif cond in trial_text_lower:
                boost += CONDITION_MATCH_BOOST * 1.5
                matched_terms.append(cond)
                hit = True
            elif cond_words and cond_words.issubset(trial_keywords):
                boost += CONDITION_MATCH_BOOST
                matched_terms.append(cond)
                hit = True
            
            if hit:
                conditions_hit += 1
                
        # Jaccard Similarity for context overlap (lightning fast)
        intersection = patient_keywords.intersection(trial_keywords)
        union = patient_keywords.union(trial_keywords)
        jaccard = len(intersection) / len(union) if union else 0.0
        
        if relevance > 0:
            # MATCHED: condition found → high score range (0.70 → 0.99)
            # Add an extra multiplier if multiple unique conditions were matched
            multi_condition_bonus = 0.10 * (conditions_hit - 1) if conditions_hit > 1 else 0.0
            
            raw_score = 0.70 + (jaccard * 0.15) + multi_condition_bonus
            final_score = min(0.99, raw_score + (boost * 0.1)) # Dampen boost to stay in range
            
            # Floor at 0.85 if at least one exact condition match
            if conditions_hit >= 1 and any(c in trial_condition_lower for c in patient_conditions_list):
                 final_score = max(0.85, final_score)
        else:
            # NOT MATCHED: no condition found → low score range (0.10 → 0.35)
            raw_score = 0.10 + (jaccard * 0.25)
            final_score = min(0.35, raw_score)
            
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
            "eligible": relevance > 0,
            "_relevance": relevance,
            "_conditions_hit": conditions_hit
        })
    
    # Sort by: 
    # 1. Number of patient conditions matched (e.g. matching both is better than one)
    # 2. Overall relevance score
    # 3. Final calculated score
    if any(m["_relevance"] > 0 for m in all_scored):
        relevant = [m for m in all_scored if m["_relevance"] > 0]
        relevant.sort(key=lambda x: (x["_conditions_hit"], x["_relevance"], x["score"]), reverse=True)
        results = relevant[:5]
    else:
        # Fallback to general keyword similarity
        all_scored.sort(key=lambda x: x["score"], reverse=True)
        for m in all_scored:
             m["explanation"] = "No direct clinical condition match found. Showing closest available symptomatic trials."
        results = all_scored[:5]
    
    # Final cleanup
    for r in results:
        r.pop("_relevance", None)
        r.pop("_conditions_hit", None)
    
    return results
