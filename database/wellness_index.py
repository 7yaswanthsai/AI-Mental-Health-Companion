from database.db_connection import get_database
import numpy as np

db = get_database()
wearable_collection = db["wearable_data"]

def compute_pwi(subject_id="S5"):
    """
    Computes a simple Personalized Wellness Index (PWI)
    based on physiological signals.
    """
    record = wearable_collection.find_one({"subject_id": subject_id})
    if not record:
        return {"subject_id": subject_id, "pwi": None, "status": "no data"}

    def normalize(val, mean_ref=0.5, std_ref=0.5):
        if val is None:
            return 0.5  # neutral value if missing
        return 1 / (1 + np.exp(-(val - mean_ref) / (std_ref + 1e-5)))  # sigmoid normalization

    # Extract key sensor means (replace with your available data)
    eda_mean = record["eda"].get("mean")
    ecg_mean = record["ecg"].get("mean")
    temp_mean = record["temp"].get("mean")
    resp_mean = record["resp"].get("mean")

    # Normalize and combine
    eda_score = normalize(eda_mean)
    ecg_score = normalize(ecg_mean)
    temp_score = normalize(temp_mean)
    resp_score = normalize(resp_mean)

    # Compute overall PWI (lower = calm, higher = stress)
    stress_level = np.mean([eda_score, ecg_score, temp_score, resp_score])

    # Interpret wellness
    if stress_level < 0.4:
        status = "calm"
    elif stress_level < 0.6:
        status = "neutral"
    else:
        status = "stressed"

    return {"subject_id": subject_id, "pwi": float(stress_level), "status": status}
