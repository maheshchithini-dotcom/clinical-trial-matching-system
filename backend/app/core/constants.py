# Scoring Logic Constants
SCORE_DECAY_FACTOR = 1.5  # Sharpened from 5.0 for better differentiation
CONDITION_MATCH_BOOST = 0.20 # Increased from 0.15 to reward direct matches more

# Confidence Thresholds
CONFIDENCE_THRESHOLD_HIGH = 0.85
CONFIDENCE_THRESHOLD_MEDIUM = 0.70

# Response Labels
CONFIDENCE_HIGH = "High"
CONFIDENCE_MEDIUM = "Medium"
CONFIDENCE_LOW = "Low"

# Medical Keywords for boost detection (extended list can be added)
COMMON_CONDITIONS = [
    "Diabetes", "Cancer", "Hypertension", "Alzheimer", "Asthma", 
    "COVID-19", "HIV", "Leukemia", "Lymphoma", "Melanoma"
]
