import os
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np

# ============================================================
# 📂 Path Setup
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
MODEL_PATH = os.path.join(BASE_DIR, "models", "emotion_lstm_model.h5")
TOKENIZER_PATH = os.path.join(BASE_DIR, "models", "tokenizer.pkl")
MLB_PATH = os.path.join(BASE_DIR, "models", "mlb.pkl")

# ============================================================
# 📦 Load Model, Tokenizer, and Label Binarizer
# ============================================================
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(TOKENIZER_PATH, "rb") as f:
        tokenizer = pickle.load(f)
    with open(MLB_PATH, "rb") as f:
        mlb = pickle.load(f)
    print("✅ Emotion model and tokenizer loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model or tokenizer: {e}")

MAX_LEN = 50  # same as training

# ============================================================
# 🔤 Preprocessing Function
# ============================================================
def preprocess_text(texts, tokenizer, max_len=MAX_LEN):
    """
    Converts input text(s) into padded token sequences.
    """
    if isinstance(texts, str):
        texts = [texts]
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=max_len, padding='post', truncating='post')
    return padded

# ============================================================
# 🔮 Emotion Prediction Function
# ============================================================
def predict_emotions(texts, threshold=0.1, top_n=3):
    """
    Predict emotions for given text(s).
    
    Args:
        texts (str or list): Input text(s)
        threshold (float): Minimum probability to consider an emotion
        top_n (int): Number of top emotions to return

    Returns:
        tuple: (list of predicted labels, list of probabilities)
    """
    X = preprocess_text(texts, tokenizer)
    probs = model.predict(X, verbose=0)

    top_labels_list, top_probs_list = [], []

    for prob in probs:
        # Get top N emotion indices
        top_indices = prob.argsort()[-top_n:][::-1]
        top_labels = [mlb.classes_[i] for i in top_indices if prob[i] >= threshold]
        top_probs = [float(prob[i]) for i in top_indices if prob[i] >= threshold]

        # Handle case with no emotions above threshold
        if not top_labels:
            top_labels = ["neutral"]
            top_probs = [float(np.mean(prob))]

        top_labels_list.append(top_labels)
        top_probs_list.append(top_probs)

    return top_labels_list, top_probs_list

# ============================================================
# 🧪 Local Demo Test
# ============================================================
if __name__ == "__main__":
    sample_text = "I feel so sad and disappointed today."
    labels, probabilities = predict_emotions(sample_text, top_n=3)

    print(f"\n🧠 Input Text: {sample_text}")
    print(f"🎭 Predicted Emotions: {labels[0]}")
    print(f"📊 Probabilities: {[round(p, 3) for p in probabilities[0]]}")
