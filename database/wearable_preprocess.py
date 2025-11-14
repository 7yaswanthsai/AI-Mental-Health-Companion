import pickle
import numpy as np
import os
from database.db_connection import get_database

db = get_database()
wearable_collection = db["wearable_data"]

def extract_features_from_pkl(pkl_path, subject_id):
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
        return {"mean": float(np.mean(arr)), "std": float(np.std(arr))}

    features = {
        "subject_id": subject_id,
        "eda": safe_stats(eda),
        "ecg": safe_stats(ecg),
        "emg": safe_stats(emg),
        "bvp": safe_stats(bvp),
        "resp": safe_stats(resp),
        "temp": safe_stats(temp),
    }

    return features


def process_all_subjects(base_path="data/wearable"):
    for subject_folder in os.listdir(base_path):
        if subject_folder.startswith("S"):
            subject_path = os.path.join(base_path, subject_folder)
            pkl_path = os.path.join(subject_path, f"{subject_folder}.pkl")

            if not os.path.exists(pkl_path):
                print(f"⚠️  No .pkl file found for {subject_folder}")
                continue

            print(f"📦 Processing {subject_folder}...")
            features = extract_features_from_pkl(pkl_path, subject_folder)
            wearable_collection.insert_one(features)
            print(f"✅ Uploaded features for {subject_folder}")


if __name__ == "__main__":
    process_all_subjects()
    print("🎉 All participants processed and uploaded successfully!")
