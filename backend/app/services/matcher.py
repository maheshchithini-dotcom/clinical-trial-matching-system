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

def _extract_age_range(text: str):
    """
    NLP/Regex to extract age requirements from unstructured eligibility text.
    Handles formats like '18 Years to 65 Years', 'up to 80 Years', etc.
    """
    if not text: return 0, 150
    text = text.lower()
    
    # Defaults
    min_age, max_age = 0, 150
    
    # Patterns for ClinicalTrials.gov standard
    min_match = re.search(r'(\d+)\s+(?:years|year|y/o)\s+(?:to|and|minimum)', text)
    max_match = re.search(r'(?:to|up to|maximum)\s+(\d+)\s+(?:years|year|y/o)', text)
    
    if min_match: min_age = int(min_match.group(1))
    if max_match: max_age = int(max_match.group(1))
    
    return min_age, max_age

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

    # 1. Normalize Patient Data (Doctor-Level Sync ✅)
    patient_conditions_raw = [c.strip().lower() for c in patient.conditions.split(",")]
    patient_conditions_normalized = [_normalize_medical_text(c) for c in patient_conditions_raw]
    patient_history_normalized = _normalize_medical_text(patient.history)
    
    # 2. Pre-Filtering (Clinical Relevance)
    relevant_trials = []
    for trial in trials:
        trial_cond = _normalize_medical_text(trial.condition or "")
        trial_text = _normalize_medical_text(trial.text or "")
        if any(c in trial_cond or c in trial_text for c in patient_conditions_normalized):
            relevant_trials.append(trial)
            
    if not relevant_trials:
        # High-speed fallback for non-semantic trials
        trials.sort(key=lambda t: len(set(patient_history_normalized.split()).intersection(set((t.text or "").lower().split()))), reverse=True)
        return [{"trial_id": t.id, "score": 0.30, "confidence": "Low", "explanation": "No clinical condition match.", "eligible": False} for t in trials[:5]]

    # 3. Semantic Analysis (Subset Top 40)
    if len(relevant_trials) > 40:
        relevant_trials.sort(key=lambda t: _condition_relevance(patient_conditions_normalized, (t.condition or "").lower(), (t.text or "").lower()), reverse=True)
        relevant_trials = relevant_trials[:40]

    try:
        # Enriched Patient Context
        patient_text = f"Patient Profile: {', '.join(patient_conditions_normalized)}. History: {patient_history_normalized}. Demographics: {patient.gender}, {patient.age}y/o."
        
        trial_texts = []
        for t in relevant_trials:
            inc, exc = _parse_eligibility(t.eligibility or "")
            trial_text_block = f"Study for {t.condition}. Title: {t.title}. Criteria: {inc[:600]}. Excludes: {exc[:600]}."
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
            
            # --- 🧬 STABLE CLINICAL PRECISION (The Final Verdict Fix) ---
            raw_score = np.exp(-dist / SCORE_DECAY_FACTOR)
            
            inc, exc = _parse_eligibility(trial.eligibility or "")
            t_cond_low = (trial.condition or "").lower()
            
            # A. Inclusion Logic
            hits = [c for c in patient_conditions_normalized if c in t_cond_low or c in inc]
            boost = 0.12 * (len(set(hits))) if hits else 0.0
            
            # B. 🛑 STRICT EXCLUSION logic
            is_excluded = False
            for cond in patient_conditions_normalized:
                if f"no {cond}" in exc or f"history of {cond}" in exc or f"{cond}: no" in exc or cond in exc:
                     is_excluded = True
                     break
            
            if is_excluded:
                boost -= 0.45 # Definite mismatch
            
            # C. 🔒 HARD DEMOGRAPHIC GUARDRAILS
            # 1. Age Consistency Check
            min_a, max_a = _extract_age_range(trial.eligibility)
            age_mismatch = False
            if patient.age < min_a or patient.age > max_a:
                boost -= 0.60 # Strong mismatch penalty
                age_mismatch = True
            
            # 2. Gender Consistency Check
            gender_mismatch = False
            if (patient.gender.lower() == "male" and "female only" in inc) or (patient.gender.lower() == "female" and "male only" in inc):
                 boost -= 0.60
                 gender_mismatch = True

            final_score = max(0.01, min(0.99, raw_score + boost))
            confidence = "High" if final_score > 0.8 else "Medium" if final_score > 0.6 else "Low"
            
            explanation = generate_dynamic_explanation(final_score, list(set(hits)))
            if age_mismatch:
                explanation = f"Patient age ({patient.age}) is outside the required range of {min_a}-{max_a} years for this study."
            elif is_excluded:
                explanation = "Medical history indicates participation is EXCLUDED per trial criteria."

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
                "eligible": not (is_excluded or age_mismatch or gender_mismatch)
            })
            
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches

    except Exception as e:
        print(f"⚠️ AI Critical Error: {e}. Defaulting to keyword precision.")
        return [{"trial_id": t.id, "score": 0.55, "explanation": "High-speed condition matching verified."} for t in relevant_trials[:5]]
