from __future__ import annotations

from typing import Dict, List, Tuple

try:
    from backend.predict_emotion import predict_emotions as lstm_predict

    _LSTM_AVAILABLE = True
except Exception:  # pragma: no cover
    lstm_predict = None  # type: ignore
    _LSTM_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

    _TRANSFORMER_AVAILABLE = True
except Exception:  # pragma: no cover
    AutoTokenizer = AutoModelForSequenceClassification = pipeline = None  # type: ignore
    _TRANSFORMER_AVAILABLE = False

MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"
TRANSFORMER_WEIGHT = 0.7
MIN_TRANSFORMER_CONF = 0.45
TOP_K_DEFAULT = 3

_classifier = None


def _load_transformer_pipeline():
    global _classifier
    if not _TRANSFORMER_AVAILABLE:
        return None
    if _classifier is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)
    return _classifier


def transformer_predict(text: str, top_n: int = TOP_K_DEFAULT) -> Tuple[List[str], List[float]]:
    classifier = _load_transformer_pipeline()
    if classifier is None:
        return [], []

    outputs = classifier(text)
    if isinstance(outputs, list) and outputs and isinstance(outputs[0], list):
        outputs = outputs[0]

    outputs = sorted(outputs, key=lambda x: x["score"], reverse=True)
    top_outputs = outputs[:top_n]
    labels = [item["label"].lower() for item in top_outputs]
    probabilities = [float(item["score"]) for item in top_outputs]
    return labels, probabilities


def lstm_predict_only(text: str, top_n: int = TOP_K_DEFAULT) -> Tuple[List[str], List[float]]:
    if not _LSTM_AVAILABLE or lstm_predict is None:
        return [], []
    try:
        labels_list, probs_list = lstm_predict(text, top_n=top_n)
        labels = labels_list[0] if labels_list else ["neutral"]
        probabilities = probs_list[0] if probs_list else [1.0]
        labels = [label.lower() for label in labels]
        return labels, [float(p) for p in probabilities]
    except Exception:
        return [], []


def _weighted_merge(
    transformer_scores: Dict[str, float],
    lstm_scores: Dict[str, float],
    tf_weight: float = TRANSFORMER_WEIGHT,
) -> Dict[str, float]:
    combined = {}
    labels = set(transformer_scores) | set(lstm_scores)
    for label in labels:
        combined[label] = tf_weight * transformer_scores.get(label, 0.0) + (1 - tf_weight) * lstm_scores.get(label, 0.0)
    return combined


def predict_emotions(text: str, top_n: int = TOP_K_DEFAULT) -> Tuple[List[str], List[float]]:
    tf_labels, tf_probs = transformer_predict(text, top_n=top_n)
    tf_conf = tf_probs[0] if tf_probs else 0.0

    lstm_labels, lstm_probs = lstm_predict_only(text, top_n=top_n)

    # If transformer confident or LSTM unavailable, return transformer result (fall back if empty)
    if tf_labels and tf_conf >= MIN_TRANSFORMER_CONF:
        return tf_labels[:top_n], tf_probs[:top_n]

    # Build score dictionaries
    tf_scores = {label: prob for label, prob in zip(tf_labels, tf_probs)}
    lstm_scores = {label: prob for label, prob in zip(lstm_labels, lstm_probs)}

    # If transformer missing completely, return LSTM
    if not tf_scores:
        if lstm_labels:
            return lstm_labels[:top_n], lstm_probs[:top_n]
        return ["neutral"], [1.0]

    combined = _weighted_merge(tf_scores, lstm_scores)
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    labels = [label for label, _ in ranked[:top_n]]
    probs = [float(score) for _, score in ranked[:top_n]]

    if not labels:
        labels = ["neutral"]
        probs = [1.0]

    return labels, probs


if __name__ == "__main__":
    sample = "I feel very sad and anxious today."
    print("Transformer:", transformer_predict(sample))
    print("LSTM:", lstm_predict_only(sample))
    print("Ensemble:", predict_emotions(sample))
