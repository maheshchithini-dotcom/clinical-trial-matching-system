import os

USE_BIOBERT = False  # Hardcoded False to prevent 502 Bad Gateway OOM on Render

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
    DEPRECATED: Embeddings are no longer used to ensure high performance on Free Tier.
    Returns a dummy list to prevent breaking legacy code if any.
    """
    return [0.0] * 384
