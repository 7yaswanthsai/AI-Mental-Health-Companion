import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"

# Load model once
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)

def predict_emotions(text, top_n=3):
    """
    Returns: (labels, probabilities)
    """
    outputs = classifier(text)

    # HF returns nested: [[{label, score}, ...]]
    if isinstance(outputs, list) and isinstance(outputs[0], list):
        outputs = outputs[0]

    # Now sort by score
    outputs = sorted(outputs, key=lambda x: x["score"], reverse=True)

    top_outputs = outputs[:top_n]
    labels = [item["label"] for item in top_outputs]
    probabilities = [float(item["score"]) for item in top_outputs]

    return labels, probabilities


# demo
if __name__ == "__main__":
    lbls, probs = predict_emotions("I feel very sad")
    print(lbls, probs)
