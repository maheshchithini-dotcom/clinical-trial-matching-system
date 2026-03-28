import os

USE_BIOBERT = os.getenv("USE_BIOBERT", "true").lower() == "true"

if USE_BIOBERT:
    from sentence_transformers import SentenceTransformer
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
    except Exception:
        USE_BIOBERT = False

# Primary embedding model – lightweight and always loaded
EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(text: str):
    """
    Generate embeddings for similarity search.
    Uses all-MiniLM-L6-v2 for both local and production.
    """
    return EMBED_MODEL.encode(text).tolist()
