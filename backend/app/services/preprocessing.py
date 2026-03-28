from transformers import AutoTokenizer, AutoModel
import torch

# Load BioBERT model for domain understanding
MODEL_NAME = "dmis-lab/biobert-v1.1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def extract_clinical_features(text: str):
    """
    Use BioBERT to understand the text and extract domain features.
    For this prototype, we'll return the pooled output as a simplified feature representation.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        
    # Get pooled output (representing the whole sequence)
    features = outputs.pooler_output[0].tolist()
    return features
