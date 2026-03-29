import os

USE_BIOBERT = False  # Hardcoded False to prevent 502 Bad Gateway OOM on Render

if USE_BIOBERT:
    try:
        import torch
        from transformers import AutoTokenizer, AutoModel
    except ImportError:
        print("⚠️ BioBERT dependencies not found. Falling back to lightweight mode.")
        USE_BIOBERT = False

# Detect environment - Render provides various environment variables
IS_PROD = os.getenv("RENDER") is not None or os.getenv("DATABASE_URL", "").startswith("postgresql://")

_EMBED_MODEL = None

def get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        # Deployment: Use all-MiniLM-L6-v2 (High Accuracy + Low Memory)
        # Local: Use BioBERT if you have the RAM
        model_name = "all-MiniLM-L6-v2" if IS_PROD else "dmis-lab/biobert-v1.1"
        try:
             print(f"📥 Loading AI Model: {model_name}...")
             _EMBED_MODEL = SentenceTransformer(model_name)
             print(f"✅ {model_name} loaded successfully.")
        except Exception as e:
             print(f"⚠️ Failed to load {model_name}: {e}. Falling back to default.")
             _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
             
    return _EMBED_MODEL

def generate_embeddings(text: str):
    """
    Generate semantic embeddings using the active model.
    """
    model = get_embed_model()
    return model.encode([text])[0].tolist()

def bulk_generate_embeddings(texts: list[str]):
    """
    Generate multiple embeddings in a single batch.
    This is significantly faster and more memory-efficient for cluster analysis.
    """
    if not texts:
        return []
    model = get_embed_model()
    # Batch size of 16 is safe for 512MB RAM
    embeddings = model.encode(texts, batch_size=16, show_progress_bar=False)
    return embeddings.tolist()
