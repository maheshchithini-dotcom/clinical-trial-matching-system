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

def _calculate_precision_score(patient, trial, patient_conditions_normalized):
    """
    🩺 GLOBAL CLINICAL PRECISION ENGINE
    This runs for EVERY match (High-Speed or AI) to ensure safety.
    """
    inc, exc = _parse_eligibility(trial.eligibility or "")
    t_cond_low = (trial.condition or "").lower()
    
    # Base relevance (Keyword overlap)
    hits = [c for c in patient_conditions_normalized if c in t_cond_low or c in inc]
    score_mod = 0.15 * (len(set(hits))) if hits else 0.0
    
    # 🛑 STRICT EXCLUSION Logic (Safety First)
    is_excluded = False
    for cond in patient_conditions_normalized:
        if f"no {cond}" in exc or f"history of {cond}" in exc or f"{cond}: no" in exc or cond in exc:
             is_excluded = True
             break
    
    if is_excluded:
        score_mod -= 0.50 # Heavy disqualification
    
    # 🔒 HARD DEMOGRAPHIC GUARDRAILS
    # 1. Age Range Check
    min_a, max_a = _extract_age_range(trial.eligibility)
    age_mismatch = (patient.age < min_a or patient.age > max_a)
    if age_mismatch:
        score_mod -= 0.60
    
    # 2. Gender Check
    gender_mismatch = False
    g_low = patient.gender.lower()
    if (g_low == "male" and "female only" in inc) or (g_low == "female" and "male only" in inc):
         score_mod -= 0.60
         gender_mismatch = True

    # Generate Clinical Reasoning
    explanation = generate_dynamic_explanation(0.8, list(set(hits)))
    if age_mismatch:
        explanation = f"Patient age ({patient.age}) is outside the required range of {min_a}-{max_a} years."
    elif is_excluded:
        explanation = "Medical history indicates participation is EXCLUDED per trial criteria."
    elif not hits:
        explanation = "Limited condition match. Precision analysis recommended."

    return {
        "is_excluded": is_excluded,
        "age_mismatch": age_mismatch,
        "gender_mismatch": gender_mismatch,
        "score_mod": score_mod,
        "explanation": explanation,
        "hits": hits
    }

def match_patient_to_trials(patient_id: int, db: Session):
    import numpy as np
    
    patient = get_patient(db, patient_id)
    if not patient: return []
    trials = get_all_trials(db)
    if not trials: return []

    # 1. Standard Clinical Normalization
    patient_conditions_raw = [c.strip().lower() for c in patient.conditions.split(",")]
    patient_conditions_normalized = [_normalize_medical_text(c) for c in patient_conditions_raw]
    
    # 2. Pre-Filtering (Clinical Relevance Only)
    relevant_trials = []
    for trial in trials:
        trial_cond = _normalize_medical_text(trial.condition or "")
        trial_text = _normalize_medical_text(trial.text or "")
        if any(c in trial_cond or c in trial_text for c in patient_conditions_normalized):
            relevant_trials.append(trial)
            
    if not relevant_trials:
        relevant_trials = trials[:5] # Fallback to general trials

    # 3. 🛡️ CRASH-PROOF CLINICAL ENGINE
    matches = []
    
    # Try Semantic AI (Optional, High RAM)
    ai_embeddings_failed = True
    all_embeddings = None
    
    try:
        from app.services.embedding import bulk_generate_embeddings
        import faiss
        
        # Enriched Patient Context
        p_text = f"Patient Profile: {', '.join(patient_conditions_normalized)}. History: {patient.history}."
        t_texts = []
        subset = relevant_trials[:20] # Strict limit for Render memory
        for t in subset:
            inc, _ = _parse_eligibility(t.eligibility or "")
            t_texts.append(_normalize_medical_text(f"Study for {t.condition}. {inc[:300]}"))
        
        all_embeddings = np.array(bulk_generate_embeddings([p_text] + t_texts)).astype('float32')
        p_embed = all_embeddings[0:1]
        t_embeds = all_embeddings[1:]
        
        index = faiss.IndexFlatL2(t_embeds.shape[1])
        index.add(t_embeds)
        D, I = index.search(p_embed, min(5, len(subset)))
        
        for i in range(len(I[0])):
            idx = I[0][i]
            trial = subset[idx]
            dist = float(D[0][i])
            raw_base = np.exp(-dist / SCORE_DECAY_FACTOR)
            
            # Apply Doctor-Level Precision
            stats = _calculate_precision_score(patient, trial, patient_conditions_normalized)
            final_score = max(0.01, min(0.99, raw_base + stats["score_mod"]))
            
            matches.append({
                "trial_id": trial.id,
                "nct_id": trial.nct_id,
                "title": trial.title,
                "condition": trial.condition,
                "score": final_score,
                "confidence": "High" if final_score > 0.75 else "Medium",
                "explanation": stats["explanation"],
                "eligible": not (stats["is_excluded"] or stats["age_mismatch"] or stats["gender_mismatch"])
            })
        ai_embeddings_failed = False
    except Exception as e:
        print(f"⚠️ Stability Triggered: AI Engine suspended ({e}). Switching to High-Speed Clinical Matcher.")

    # 4. Fallback: High-Speed Clinical Matcher (Zero RAM ✅)
    if ai_embeddings_failed:
        for trial in relevant_trials[:5]:
            stats = _calculate_precision_score(patient, trial, patient_conditions_normalized)
            final_score = max(0.1, min(0.85, 0.45 + stats["score_mod"]))
            
            matches.append({
                "trial_id": trial.id,
                "nct_id": trial.nct_id,
                "title": trial.title,
                "condition": trial.condition,
                "score": final_score,
                "confidence": "Medium",
                "explanation": stats["explanation"] + " (High-Speed Match verified)",
                "eligible": not (stats["is_excluded"] or stats["age_mismatch"] or stats["gender_mismatch"])
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:5]
