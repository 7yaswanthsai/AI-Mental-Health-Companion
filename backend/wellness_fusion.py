import numpy as np
from datetime import datetime
from database.db_connection import get_database

# Connect to MongoDB
db = get_database()
wearable_data = db["wearable_data"]
wearable_baselines = db["wearable_baselines"]

# Feature weights (tunable)
FEATURE_WEIGHTS = {
    "eda": 0.25,
    "temp": 0.15,
    "bvp": 0.20,
    "ecg": 0.20,
    "resp": 0.20,
}

# EMA smoothing factor (alpha)
EMA_ALPHA = 0.3

# PWI thresholds
PWI_THRESHOLDS = {
    "Calm": 70,
    "Neutral": 40,
    "Mild Stress": 30,
    "Stressed": 0,
}


def safe_mean(value_dict):
    """Safely extract mean value or return None."""
    if isinstance(value_dict, dict):
        mean_val = value_dict.get("mean")
        return float(mean_val) if mean_val is not None else None
    return None


def safe_std(value_dict):
    """Safely extract std value or return None."""
    if isinstance(value_dict, dict):
        std_val = value_dict.get("std")
        return float(std_val) if std_val is not None else None
    return None


def compute_hrv_rmssd(ecg_signal, sampling_rate=700):
    """Compute HRV RMSSD from ECG signal (simplified)."""
    if ecg_signal is None or len(ecg_signal) < 2:
        return None
    try:
        # Simplified: use std of signal as proxy for HRV
        # In production, would detect R-peaks and compute RR intervals
        return float(np.std(ecg_signal))
    except Exception:
        return None


def compute_eda_peaks(eda_signal, threshold_percentile=75):
    """Count EDA peaks above threshold (simplified)."""
    if eda_signal is None or len(eda_signal) < 10:
        return None
    try:
        threshold = np.percentile(eda_signal, threshold_percentile)
        peaks = np.sum(eda_signal > threshold)
        return float(peaks / len(eda_signal))  # Normalized peak rate
    except Exception:
        return None


def get_or_compute_baseline(subject_id: str, window_days: int = 7):
    """Get baseline stats for subject, or compute from historical data."""
    baseline = wearable_baselines.find_one({"subject_id": subject_id})
    if baseline:
        return baseline

    # Compute baseline from existing data (if available)
    subject_data = wearable_data.find_one({"subject_id": subject_id})
    if not subject_data:
        return None

    # Use current data as baseline (in production, would aggregate over time window)
    baseline_stats = {
        "subject_id": subject_id,
        "eda": {"mean": safe_mean(subject_data.get("eda")), "std": safe_std(subject_data.get("eda"))},
        "temp": {"mean": safe_mean(subject_data.get("temp")), "std": safe_std(subject_data.get("temp"))},
        "bvp": {"mean": safe_mean(subject_data.get("bvp")), "std": safe_std(subject_data.get("bvp"))},
        "ecg": {"mean": safe_mean(subject_data.get("ecg")), "std": safe_std(subject_data.get("ecg"))},
        "resp": {"mean": safe_mean(subject_data.get("resp")), "std": safe_std(subject_data.get("resp"))},
        "computed_at": datetime.utcnow(),
    }

    # Store baseline
    wearable_baselines.insert_one(baseline_stats)
    return baseline_stats


def normalize_feature(value, baseline_mean, baseline_std, inverse=False):
    """Normalize feature using z-score relative to baseline."""
    if value is None or baseline_mean is None or baseline_std is None or baseline_std == 0:
        return 0.5  # Neutral value

    z_score = (value - baseline_mean) / baseline_std

    # For stress indicators (EDA, TEMP, RESP), higher = more stress
    # For calm indicators (BVP, ECG), higher = more calm
    if inverse:
        z_score = -z_score  # Invert for calm indicators

    # Transform z-score to [0, 1] using sigmoid
    normalized = 1 / (1 + np.exp(-z_score))
    return float(normalized)


def apply_ema_smoothing(current_value, previous_value, alpha=EMA_ALPHA):
    """Apply exponential moving average smoothing."""
    if previous_value is None:
        return current_value
    return alpha * current_value + (1 - alpha) * previous_value


def compute_pwi(subject_id: str, use_smoothing: bool = True):
    """
    Compute Personalized Wellness Index with baseline normalization and smoothing.
    
    Args:
        subject_id: Subject identifier
        use_smoothing: Whether to apply EMA smoothing (requires previous PWI in session)
    
    Returns:
        dict with pwi, status, features, and metadata
    """
    subject = wearable_data.find_one({"subject_id": subject_id})
    if not subject:
        return {
            "subject_id": subject_id,
            "pwi": None,
            "status": "Unknown (No Data)",
            "features": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Get or compute baseline
    baseline = get_or_compute_baseline(subject_id)
    if not baseline:
        return {
            "subject_id": subject_id,
            "pwi": None,
            "status": "Unknown (No Data)",
            "features": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Extract raw features
    eda_mean = safe_mean(subject.get("eda"))
    temp_mean = safe_mean(subject.get("temp"))
    bvp_mean = safe_mean(subject.get("bvp"))
    ecg_mean = safe_mean(subject.get("ecg"))
    resp_mean = safe_mean(subject.get("resp"))

    # Check if all features are missing
    feature_values = [eda_mean, temp_mean, bvp_mean, ecg_mean, resp_mean]
    if all(v is None for v in feature_values):
        return {
            "subject_id": subject_id,
            "pwi": None,
            "status": "Unknown (No Data)",
            "features": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Normalize features relative to baseline
    eda_norm = normalize_feature(eda_mean, baseline["eda"]["mean"], baseline["eda"]["std"], inverse=False)
    temp_norm = normalize_feature(temp_mean, baseline["temp"]["mean"], baseline["temp"]["std"], inverse=False)
    bvp_norm = normalize_feature(bvp_mean, baseline["bvp"]["mean"], baseline["bvp"]["std"], inverse=True)
    ecg_norm = normalize_feature(ecg_mean, baseline["ecg"]["mean"], baseline["ecg"]["std"], inverse=True)
    resp_norm = normalize_feature(resp_mean, baseline["resp"]["mean"], baseline["resp"]["std"], inverse=False)

    # Weighted combination
    stress_components = (
        FEATURE_WEIGHTS["eda"] * eda_norm
        + FEATURE_WEIGHTS["temp"] * temp_norm
        + FEATURE_WEIGHTS["resp"] * resp_norm
    )
    calm_components = FEATURE_WEIGHTS["bvp"] * bvp_norm + FEATURE_WEIGHTS["ecg"] * ecg_norm

    # Compute raw PWI (0-100 scale, higher = better wellness)
    raw_pwi = (1 - stress_components) * 0.6 + calm_components * 0.4
    pwi = float(np.clip(raw_pwi * 100, 0, 100))

    # Determine status
    if pwi >= PWI_THRESHOLDS["Calm"]:
        status = "Calm"
    elif pwi >= PWI_THRESHOLDS["Neutral"]:
        status = "Neutral"
    elif pwi >= PWI_THRESHOLDS["Mild Stress"]:
        status = "Mild Stress"
    else:
        status = "Stressed"

    result = {
        "subject_id": subject_id,
        "pwi": round(pwi, 2),
        "status": status,
        "features": {
            "eda": round(eda_mean, 3) if eda_mean is not None else None,
            "temp": round(temp_mean, 3) if temp_mean is not None else None,
            "bvp": round(bvp_mean, 3) if bvp_mean is not None else None,
            "ecg": round(ecg_mean, 3) if ecg_mean is not None else None,
            "resp": round(resp_mean, 3) if resp_mean is not None else None,
        },
        "normalized_features": {
            "eda": round(eda_norm, 3),
            "temp": round(temp_norm, 3),
            "bvp": round(bvp_norm, 3),
            "ecg": round(ecg_norm, 3),
            "resp": round(resp_norm, 3),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    return result


if __name__ == "__main__":
    result = compute_pwi("S10")
    if result:
        print("\n✅ Final PWI Result:")
        print(f"  Subject: {result['subject_id']}")
        print(f"  PWI: {result['pwi']}")
        print(f"  Status: {result['status']}")
        print(f"  Features: {result['features']}")
