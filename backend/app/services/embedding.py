from sentence_transformers import SentenceTransformer

# Load a medical-domain-specific sentence transformer if possible, 
# but for matching, a general medical one works well.
EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2') 

def generate_embeddings(text: str):
    """
    Generate embeddings for similarity search using Sentence Transformers.
    """
    return EMBED_MODEL.encode(text).tolist()
