import os

USE_BIOBERT = os.getenv("USE_BIOBERT", "true").lower() == "true"

if USE_BIOBERT:
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch

        MODEL_NAME = "dmis-lab/biobert-v1.1"
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModel.from_pretrained(MODEL_NAME)
        print("✅ BioBERT loaded for clinical feature extraction.")
    except Exception as e:
        print(f"⚠️ BioBERT failed to load: {e}. Falling back to lightweight mode.")
        USE_BIOBERT = False

def extract_clinical_features(text: str):
    """
    Use BioBERT (if available) to extract domain features from clinical text.
    Falls back gracefully when USE_BIOBERT=false (production/cloud deployment).
    """
    if not USE_BIOBERT:
        # Lightweight fallback: return a simple keyword representation
        return text.lower()

    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = _model(**inputs)

    features = outputs.pooler_output[0].tolist()
    return features
