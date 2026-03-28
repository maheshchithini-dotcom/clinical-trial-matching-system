import requests
from sqlalchemy.orm import Session
from app.db.models import Trial
from app.core.config import settings

def fetch_trials_from_api(db: Session, query: str = "diabetes"):
    """
    Fetch clinical trials from ClinicalTrials.gov API v2.
    """
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.term": query,
        "pageSize": settings.MAX_TRIALS_TO_SYNC,
        "fields": "NCTId,BriefTitle,Condition,BriefSummary,EligibilityModule"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        trials_added = 0
        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            id_info = protocol.get("identificationModule", {})
            status_info = protocol.get("statusModule", {}) # for future use
            conditions_module = protocol.get("conditionsModule", {})
            description_module = protocol.get("descriptionModule", {})
            eligibility_module = protocol.get("eligibilityModule", {})

            nct_id = id_info.get("nctId")
            title = id_info.get("briefTitle")
            
            # Extract clinical text
            condition = ", ".join(conditions_module.get("conditions", []))
            summary = description_module.get("briefSummary", "No summary available.")
            eligibility = eligibility_module.get("eligibilityCriteria", "No criteria specified.")

            # Check if exists
            existing = db.query(Trial).filter(Trial.nct_id == nct_id).first()
            if not existing:
                trial = Trial(
                    nct_id=nct_id,
                    title=title,
                    condition=condition,
                    text=summary,
                    eligibility=eligibility
                )
                db.add(trial)
                trials_added += 1

        db.commit()
        return trials_added

    except Exception as e:
        print(f"Sync failed: {str(e)}")
        db.rollback()
        return 0
