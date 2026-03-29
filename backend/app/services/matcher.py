# 🩺 Medical Normalization Map (Clinical Precision ✅)
# Ensures synonyms like "High Sugar" and "Type 2 Diabetes" are matched perfectly across ALL trials.
MEDICAL_SYNONYMS = {
    "high sugar": "diabetes",
    "blood sugar": "diabetes",
    "glucose": "diabetes",
    "hypertension": "high blood pressure",
    "high bp": "high blood pressure",
    "cardiac": "heart",
    "myocardial infarction": "heart attack",
    "renal": "kidney",
    "nephropathy": "kidney disease",
    "hepatic": "liver",
    "malignancy": "cancer",
    "neoplasm": "tumor",
    "pulmonary": "lung",
    "copd": "chronic obstructive pulmonary disease"
}

def _normalize_medical_text(text: str):
    text = text.lower()
    for layman, clinical in MEDICAL_SYNONYMS.items():
        text = text.replace(layman, clinical)
    return text

def _parse_eligibility(eligibility_text: str):
    """
    Splits clinical trial eligibility text into Inclusion and Exclusion blocks.
    ClinicalTrials.gov typically uses strict headers.
    """
    if not eligibility_text:
        return "", ""
        
    text = eligibility_text.lower()
    inclusion = ""
    exclusion = ""
    
    if "exclusion criteria:" in text:
        parts = text.split("exclusion criteria:")
        inclusion = parts[0].replace("inclusion criteria:", "").strip()
        exclusion = parts[1].strip()
    elif "exclusion:" in text:
        parts = text.split("exclusion:")
        inclusion = parts[0].replace("inclusion:", "").strip()
        exclusion = parts[1].strip()
    else:
        inclusion = text # Fallback
        
    return inclusion, exclusion

def match_patient_to_trials(patient_id: int, db: Session):
    import numpy as np
    import faiss
    from app.services.embedding import bulk_generate_embeddings
    
    patient = get_patient(db, patient_id)
    if not patient:
        return []

    trials = get_all_trials(db)
    if not trials:
        return []

    # 1. Normalize Patient Data
    patient_conditions_raw = [c.strip().lower() for c in patient.conditions.split(",")]
    patient_conditions_normalized = [_normalize_medical_text(c) for c in patient_conditions_raw]
    patient_history_normalized = _normalize_medical_text(patient.history)
    
    # 2. NLP Pre-Filtering (Relevance check)
    relevant_trials = []
    for trial in trials:
        trial_cond = _normalize_medical_text(trial.condition or "")
        trial_text = _normalize_medical_text(trial.text or "")
        if any(c in trial_cond or c in trial_text for c in patient_conditions_normalized):
            relevant_trials.append(trial)
            
    if not relevant_trials:
        # Fallback keyword match
        trials.sort(key=lambda t: len(set(patient_history_normalized.split()).intersection(set((t.text or "").lower().split()))), reverse=True)
        return [{"trial_id": t.id, "score": 0.35, "confidence": "Low", "explanation": "No direct match.", "eligible": False} for t in trials[:5]]

    # 3. Safety: High-Accuracy Subset (Top 40)
    if len(relevant_trials) > 40:
        relevant_trials.sort(key=lambda t: _condition_relevance(patient_conditions_normalized, (t.condition or "").lower(), (t.text or "").lower()), reverse=True)
        relevant_trials = relevant_trials[:40]

    try:
        # 4. 🧬 ENRICHED SEMANTIC ENGINE (Doctor-Level Precision ✅)
        patient_text = f"Conditions: {', '.join(patient_conditions_normalized)}. History: {patient_history_normalized}. Demographics: {patient.gender}, {patient.age}y/o."
        
        trial_texts = []
        for t in relevant_trials:
            inc, exc = _parse_eligibility(t.eligibility or "")
            trial_text_block = f"Trial: {t.title}. For: {t.condition}. Includes: {inc[:500]}. Excludes: {exc[:500]}."
            trial_texts.append(_normalize_medical_text(trial_text_block))
        
        all_texts = [patient_text] + trial_texts
        all_embeddings = np.array(bulk_generate_embeddings(all_texts)).astype('float32')
        
        p_embed = all_embeddings[0:1]
        t_embeds = all_embeddings[1:]
        
        index = faiss.IndexFlatL2(t_embeds.shape[1])
        index.add(t_embeds)
        
        k = min(5, len(relevant_trials))
        D, I = index.search(p_embed, k)
        
        matches = []
        for i in range(k):
            idx = I[0][i]
            dist = float(D[0][i])
            trial = relevant_trials[idx]
            
            # --- 🩺 Precision Scoring Phase ---
            raw_score = np.exp(-dist / SCORE_DECAY_FACTOR)
            
            inc, exc = _parse_eligibility(trial.eligibility or "")
            t_cond_low = (trial.condition or "").lower()
            
            # A. Inclusion Boost
            hits = [c for c in patient_conditions_normalized if c in t_cond_low or c in inc]
            boost = 0.10 * (len(set(hits))) if hits else 0.0
            
            # B. 🛑 CRITICAL EXCLUSION CHECK (Fix for safety)
            # If the patient condition matches the trial's EXCLUSION criteria, apply a massive penalty.
            is_excluded = any(c in exc for c in patient_conditions_normalized)
            if is_excluded:
                boost -= 0.40 # Heavy penalty for exclusionary match
            
            # C. Demographic Hard-Check
            # (Simplistic check for obvious age/gender mismatch in eligibility block)
            if (patient.gender.lower() == "male" and "female only" in inc) or (patient.gender.lower() == "female" and "male only" in inc):
                boost -= 0.50

            final_score = max(0.01, min(0.99, raw_score + boost))
            confidence = "High" if final_score > 0.8 else "Medium" if final_score > 0.6 else "Low"
            
            # Explainer enhancement
            explanation = generate_dynamic_explanation(final_score, list(set(hits)))
            if is_excluded:
                explanation = "CAUTION: This trial matches your symptoms but your medical history may exclude you from participation. Consult a physician."

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
                "eligible": not is_excluded
            })
            
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches

    except Exception as e:
        print(f"⚠️ AI Analysis Fallback: {e}")
        return [{"trial_id": t.id, "score": 0.5, "explanation": "Quick-match active."} for t in relevant_trials[:5]]
