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
    import numpy as np
    import faiss
    
    patient = get_patient(db, patient_id)
    if not patient:
        return []

    trials = get_all_trials(db)
    if not trials:
        return []

    patient_conditions_list = [c.strip().lower() for c in patient.conditions.split(",")]
    
    # 1. Strict NLP Pre-Filtering
    relevant_trials = []
    fallback_trials = []
    
    for trial in trials:
        trial_condition_lower = trial.condition.lower() if trial.condition else ""
        trial_text_lower = trial.text.lower() if trial.text else ""
        
        relevance = _condition_relevance(patient_conditions_list, trial_condition_lower, trial_text_lower)
        if relevance > 0:
            relevant_trials.append(trial)
        else:
            fallback_trials.append(trial)
            
    # If no relevant trials found, return fallback based on simple heuristics
    if not relevant_trials:
        fallback_trials.sort(key=lambda t: len(set(patient.history.lower().split()).intersection(set((t.text or "").lower().split()))), reverse=True)
        results = []
        for t in fallback_trials[:5]:
            results.append({
                "trial_id": t.id,
                "nct_id": t.nct_id,
                "title": t.title or "Untitled Study",
                "condition": t.condition,
                "text": t.text,
                "eligibility": t.eligibility,
                "score": 0.35,
                "confidence": "Low",
                "explanation": "No direct condition match found. Showing closest available trials.",
                "eligible": False
            })
        return results

    # 2. Semantic Search (Sentence Transformers + FAISS) ONLY on relevant trials
    patient_text = f"Patient is a {patient.age}-year-old {patient.gender}. Diagnosed conditions: {patient.conditions}. Clinical history: {patient.history}."
    
    trial_texts = []
    for t in relevant_trials:
        enriched_text = f"Title: {t.title or t.nct_id}. Conditions: {t.condition}. Summary: {t.text}. Eligibility: {t.eligibility or 'Not specified'}."
        trial_texts.append(enriched_text)
        
    # Generate embeddings utilizing all-MiniLM-L6-v2 (BioBERT is disabled)
    trial_embeddings = np.array([generate_embeddings(text) for text in trial_texts]).astype('float32')
    dimension = trial_embeddings.shape[1]
    
    index = faiss.IndexFlatL2(dimension)
    index.add(trial_embeddings)
    
    patient_embedding = np.array([generate_embeddings(patient_text)]).astype('float32')
    
    k = min(5, len(relevant_trials))
    D, I = index.search(patient_embedding, k)
    
    matches = []
    for i in range(k):
        idx = I[0][i]
        dist = float(D[0][i])
        
        # Exponential Scoring from L2 distance
        raw_score = np.exp(-dist / SCORE_DECAY_FACTOR) 
        trial = relevant_trials[idx]
        trial_condition_lower = trial.condition.lower() if trial.condition else ""
        trial_text_lower = trial.text.lower() if trial.text else ""
        
        # Apply condition boost
        boost = 0.0
        matched_terms = []
        for cond in patient_conditions_list:
            if cond in trial_condition_lower:
                boost += CONDITION_MATCH_BOOST * 2.0
                matched_terms.append(cond)
            elif cond in trial_text_lower:
                boost += CONDITION_MATCH_BOOST * 1.5
                matched_terms.append(cond)
        
        # Ensure scores are within 0-1 bounds and boosted correctly
        final_score = min(0.99, raw_score + boost)
        if boost >= (CONDITION_MATCH_BOOST * 2.0):
            final_score = max(0.85, final_score)
            
        confidence = get_confidence_level(final_score)
        explanation = generate_dynamic_explanation(final_score, list(set(matched_terms)))

        matches.append({
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
        
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches
