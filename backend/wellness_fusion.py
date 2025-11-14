import numpy as np
from database.db_connection import get_database

# Connect to MongoDB
db = get_database()
wearable_data = db["wearable_data"]

def safe_mean(value_dict):
    """Safely extract mean value or return 0."""
    if isinstance(value_dict, dict):
        mean_val = value_dict.get("mean", 0.0)
        return float(mean_val) if mean_val is not None else 0.0
    return 0.0

def compute_pwi(subject_id: str):
    """Compute Personalized Wellness Index for given subject."""
    subject = wearable_data.find_one({"subject_id": subject_id})
    if not subject:
        print(f"⚠️ Subject {subject_id} not found in MongoDB.")
        return {
            "subject_id": subject_id,
            "status": "no data",
            "pwi": None,
            "features": {},
        }

    # Extract physiological features
    eda_mean = safe_mean(subject.get("eda"))
    temp_mean = safe_mean(subject.get("temp"))
    bvp_mean = safe_mean(subject.get("bvp"))
    ecg_mean = safe_mean(subject.get("ecg"))
    resp_mean = safe_mean(subject.get("resp"))

    print(f"📊 Extracted Features from {subject_id} -> "
          f"EDA: {eda_mean}, TEMP: {temp_mean}, BVP: {bvp_mean}, ECG: {ecg_mean}, RESP: {resp_mean}")

    # Normalize each feature (avoid division by zero or unrealistic values)
    eda_norm = min(max(eda_mean / 10, 0), 1.0)
    temp_norm = min(max((temp_mean - 30) / 10, 0), 1.0)
    bvp_norm = min(max(bvp_mean / 100, 0), 1.0)
    ecg_norm = min(max(ecg_mean / 200, 0), 1.0)
    resp_norm = min(max(resp_mean / 20, 0), 1.0)

    # If all values are 0, return baseline
    feature_values = [eda_mean, temp_mean, bvp_mean, ecg_mean, resp_mean]
    if all(v == 0 or v is None for v in feature_values):
        pwi = 50.0
        status = "unknown"
    else:
        # Compute stress factor (higher EDA/temp/resp = more stress)
        stress_factor = (eda_norm + temp_norm + resp_norm) / 3
        calm_factor = (bvp_norm + ecg_norm) / 2

        # Weighted formula for PWI
        pwi = (1 - stress_factor) * 0.6 + calm_factor * 0.4
        pwi = round(pwi * 100, 2)
        pwi = min(max(pwi, 0), 100)

        status = (
            "Calm" if pwi > 70 else
            "Mild Stress" if pwi > 40 else
            "Stressed"
        )

    result = {
        "subject_id": subject_id,
        "pwi": pwi,
        "status": status,
        "features": {
            "eda": round(eda_mean, 3) if eda_mean is not None else None,
            "temp": round(temp_mean, 3) if temp_mean is not None else None,
            "bvp": round(bvp_mean, 3) if bvp_mean is not None else None,
            "ecg": round(ecg_mean, 3) if ecg_mean is not None else None,
            "resp": round(resp_mean, 3) if resp_mean is not None else None,
        },
    }

    print(f"\n✅ Wellness Index Computed for {subject_id}: {result}")
    return result

if __name__ == "__main__":
    result = compute_pwi("S10")
    if result:
        print("\nFinal PWI Result:", result)
