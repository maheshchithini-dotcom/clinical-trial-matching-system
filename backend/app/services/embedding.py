import os

USE_BIOBERT = os.getenv("USE_BIOBERT", "true").lower() == "true"

if USE_BIOBERT:
    try:
        import torch
        from transformers import AutoTokenizer, AutoModel
    except ImportError:
        print("⚠️ BioBERT dependencies not found. Falling back to lightweight mode.")
        USE_BIOBERT = False

# Primary embedding model – loaded lazily to prevent startup timeouts
_EMBED_MODEL = None

def get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        print("📥 Loading embedding model (all-MiniLM-L6-v2)...")
        _EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded.")
    return _EMBED_MODEL

def generate_embeddings(text: str):
    """
    Generate embeddings for similarity search.
    Uses all-MiniLM-L6-v2 for both local and production.
    """
    model = get_embed_model()
    return model.encode(text).tolist()
