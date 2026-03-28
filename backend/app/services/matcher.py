from sqlalchemy.orm import Session
from app.db.crud import get_patient, get_all_trials
from app.services.preprocessing import extract_clinical_features
from app.services.embedding import generate_embeddings
from app.services.explainer import generate_dynamic_explanation, get_confidence_level
from app.core.constants import SCORE_DECAY_FACTOR, CONDITION_MATCH_BOOST

def match_patient_to_trials(patient_id: int, db: Session):
    # Move heavy imports here so they don't block app startup
    import faiss
    import numpy as np
    patient = get_patient(db, patient_id)
    if not patient:
        return []

    trials = get_all_trials(db)
    if not trials:
        return []

    # 1. Enrich Patient Representation
    patient_conditions_list = [c.strip() for c in patient.conditions.split(",")]
    patient_text = (
        f"Patient is a {patient.age}-year-old {patient.gender}. "
        f"Diagnosed conditions: {patient.conditions}. "
        f"Clinical history: {patient.history}."
    )
    
    # 2. Enrich Trial Representations
    trial_ids = [t.id for t in trials]
    trial_texts = []
    for t in trials:
        enriched_text = (
            f"Title: {t.title or t.nct_id}. "
            f"Conditions: {t.condition}. "
            f"Summary: {t.text}. "
            f"Eligibility: {t.eligibility or 'Not specified'}."
        )
        trial_texts.append(enriched_text)
    
    # 3. Generate Embeddings & FAISS Index
    trial_embeddings = np.array([generate_embeddings(text) for text in trial_texts]).astype('float32')
    dimension = trial_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(trial_embeddings)
    
    patient_embedding = np.array([generate_embeddings(patient_text)]).astype('float32')
    
    k = min(10, len(trial_ids))
    D, I = index.search(patient_embedding, k)
    
    matches = []
    for i in range(k):
        idx = I[0][i]
        dist = float(D[0][i])
        
        # 4. Exponential Scoring
        raw_score = np.exp(-dist / SCORE_DECAY_FACTOR) 
        
        trial = trials[idx]
        trial_condition_lower = trial.condition.lower()
        
        # 5. Condition Boost
        boost = 0.0
        matched_terms = []
        for cond in patient_conditions_list:
            if cond.lower() in trial_condition_lower:
                boost += CONDITION_MATCH_BOOST
                matched_terms.append(cond)
        
        final_score = min(1.0, raw_score + boost)
        
        # 6. Confidence & Dynamic Explanation (Delegated to service)
        confidence = get_confidence_level(final_score)
        explanation = generate_dynamic_explanation(final_score, matched_terms)

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
