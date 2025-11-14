import pickle
import numpy as np
import os
from datetime import datetime
from database.db_connection import get_database

db = get_database()
wearable_collection = db["wearable_data"]
wearable_baselines = db["wearable_baselines"]


def extract_features_from_pkl(pkl_path, subject_id):
    """Extract features from WESAD pickle file."""
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f, encoding='latin1')

    # Access the correct structure
    signals = data.get('signal', {})
    
    # Each sensor signal is a NumPy array
    eda = signals.get('EDA')
    ecg = signals.get('ECG')
    emg = signals.get('EMG')
    temp = signals.get('Temp')
    bvp = signals.get('BVP')
    resp = signals.get('Resp')

    # Compute mean and std safely
    def safe_stats(arr):
        if arr is None or not len(arr):
            return {"mean": None, "std": None}
        arr_clean = np.array(arr)
        arr_clean = arr_clean[~np.isnan(arr_clean)]
        if len(arr_clean) == 0:
            return {"mean": None, "std": None}
        return {"mean": float(np.mean(arr_clean)), "std": float(np.std(arr_clean))}

    features = {
        "subject_id": subject_id,
        "eda": safe_stats(eda),
        "ecg": safe_stats(ecg),
        "emg": safe_stats(emg),
        "bvp": safe_stats(bvp),
        "resp": safe_stats(resp),
        "temp": safe_stats(temp),
        "processed_at": datetime.utcnow(),
    }

    return features


def compute_baseline_from_features(features):
    """Compute baseline statistics from extracted features."""
    baseline = {
        "subject_id": features["subject_id"],
        "eda": features.get("eda", {}),
        "temp": features.get("temp", {}),
        "bvp": features.get("bvp", {}),
        "ecg": features.get("ecg", {}),
        "resp": features.get("resp", {}),
        "computed_at": datetime.utcnow(),
    }
    return baseline


def process_all_subjects(base_path="data/wearable", compute_baselines=True):
    """
    Process all subject folders and extract features.
    
    Args:
        base_path: Base path to wearable data directory
        compute_baselines: Whether to compute and store baseline statistics
    """
    processed_count = 0
    baseline_count = 0

    for subject_folder in os.listdir(base_path):
        if not subject_folder.startswith("S"):
            continue

        subject_path = os.path.join(base_path, subject_folder)
        pkl_path = os.path.join(subject_path, f"{subject_folder}.pkl")

        if not os.path.exists(pkl_path):
            print(f"⚠️  No .pkl file found for {subject_folder}")
            continue

        print(f"📦 Processing {subject_folder}...")
        
        try:
            # Extract features
            features = extract_features_from_pkl(pkl_path, subject_folder)
            
            # Check if subject already exists
            existing = wearable_collection.find_one({"subject_id": subject_folder})
            if existing:
                # Update existing record
                wearable_collection.update_one(
                    {"subject_id": subject_folder},
                    {"$set": features}
                )
                print(f"  ✅ Updated features for {subject_folder}")
            else:
                # Insert new record
                wearable_collection.insert_one(features)
                print(f"  ✅ Inserted features for {subject_folder}")
            
            processed_count += 1

            # Compute and store baseline if requested
            if compute_baselines:
                baseline = compute_baseline_from_features(features)
                existing_baseline = wearable_baselines.find_one({"subject_id": subject_folder})
                
                if existing_baseline:
                    wearable_baselines.update_one(
                        {"subject_id": subject_folder},
                        {"$set": baseline}
                    )
                    print(f"  ✅ Updated baseline for {subject_folder}")
                else:
                    wearable_baselines.insert_one(baseline)
                    print(f"  ✅ Stored baseline for {subject_folder}")
                    baseline_count += 1

        except Exception as e:
            print(f"  ❌ Error processing {subject_folder}: {e}")
            continue

    print(f"\n🎉 Processing complete!")
    print(f"  Processed subjects: {processed_count}")
    print(f"  Baselines computed: {baseline_count}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process WESAD wearable data")
    parser.add_argument("--base-path", default="data/wearable", help="Base path to wearable data")
    parser.add_argument("--no-baselines", action="store_true", help="Skip baseline computation")
    args = parser.parse_args()
    
    process_all_subjects(
        base_path=args.base_path,
        compute_baselines=not args.no_baselines
    )
