import sys
import os
import faiss
import numpy as np
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.crud import get_all_trials
from app.services.embedding import generate_embeddings

def build_and_save_index():
    """
    Standalone script to pre-calculate embeddings and build a FAISS index.
    Useful for production deployment to avoid on-the-fly indexing.
    """
    db = SessionLocal()
    try:
        trials = get_all_trials(db)
        if not trials:
            print("No trials found in database.")
            return

        print(f"Generating embeddings for {len(trials)} trials...")
        trial_texts = []
        for t in trials:
            enriched_text = (
                f"Title: {t.title or t.nct_id}. "
                f"Conditions: {t.condition}. "
                f"Summary: {t.text}. "
                f"Eligibility: {t.eligibility or 'Not specified'}."
            )
            trial_texts.append(enriched_text)
        
        embeddings = np.array([generate_embeddings(text) for text in trial_texts]).astype('float32')
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # Save the index to a file
        faiss.write_index(index, "clinical_trials.index")
        print("Success: FAISS index built and saved to 'clinical_trials.index'")

    finally:
        db.close()

if __name__ == "__main__":
    build_and_save_index()
