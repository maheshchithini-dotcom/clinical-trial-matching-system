import os

USE_BIOBERT = False  # Hardcoded False to prevent 502 Bad Gateway OOM on Render

# Global model containers for lazy loading
_tokenizer = None
_model = None

def load_biobert():
    global _tokenizer, _model
    if _tokenizer is None:
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            MODEL_NAME = "dmis-lab/biobert-v1.1"
            print(f"📥 Loading BioBERT ({MODEL_NAME})...")
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            _model = AutoModel.from_pretrained(MODEL_NAME)
            print("✅ BioBERT loaded.")
        except ImportError:
            return False
    return True

def extract_clinical_features(text: str):
    """
    Use BioBERT (if available) to extract domain features from clinical text.
    Falls back gracefully when USE_BIOBERT=false (production/cloud deployment).
    """
    global USE_BIOBERT
    if not USE_BIOBERT or not load_biobert():
        # Lightweight fallback
        return text.lower()

    import torch
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = _model(**inputs)

    features = outputs.pooler_output[0].tolist()
    return features
