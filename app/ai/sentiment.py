import json
from datetime import datetime
from transformers import pipeline

# Load models once (cached in container)
sentiment_model = pipeline("sentiment-analysis")
core_value_model = pipeline("zero-shot-classification")

# Sacumen core values
CORE_VALUES = ["Customer delight", "Innovation", "Team work", "Being fair", "Ownership"]

# ----------------------------
# Step 1: Load nominations JSON
# ----------------------------
def load_nominations(file_path="employee_nominations.json"):
    """
    Load nominations from a JSON file
    """
    with open(file_path, "r") as f:
        return json.load(f)

# ----------------------------
# Step 2: Preprocess comment
# ----------------------------
def preprocess_comment(comment: str):
    """
    Simple cleaning: strip whitespace
    """
    return comment.strip()

# ----------------------------
# Step 3: Analyze single nomination
# ----------------------------
def analyze_nomination(nomination: dict):
    """
    Runs sentiment analysis and core-value alignment
    Input: {
        "nomination_id": int,
        "employee_id": int,
        "manager_id": int,
        "core_value_claimed": str,
        "comment": str
    }
    Output: dict with sentiment & alignment results
    """
    comment = preprocess_comment(nomination["comment"])
    
    # Sentiment analysis
    sentiment = sentiment_model(comment)[0]  # {'label': 'POSITIVE', 'score': 0.95}
    
    # Zero-shot classification for core value
    core_value_pred = core_value_model(comment, CORE_VALUES)
    predicted_value = core_value_pred["labels"][0]
    
    # Compute alignment score
    match_score = 100 if predicted_value == nomination["core_value_claimed"] else 50
    if sentiment["label"] != "POSITIVE":
        match_score -= 20
    
    return {
        "nomination_id": nomination["nomination_id"],
        "employee_id": nomination["employee_id"],
        "manager_id": nomination["manager_id"],
        "sentiment_label": sentiment["label"],
        "sentiment_score": float(sentiment["score"]),
        "predicted_core_value": predicted_value,
        "core_value_alignment": match_score,
        "analyzed_at": datetime.now()
    }

# ----------------------------
# Step 4: Analyze list of nominations
# ----------------------------
def analyze_all_nominations(file_path="employee_nominations.json"):
    nominations = load_nominations(file_path)
    results = [analyze_nomination(n) for n in nominations]
    return results


load_json = load_nominations