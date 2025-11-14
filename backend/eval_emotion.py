import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score

from backend.emotion_service import (
    lstm_predict_only,
    predict_emotions,
    transformer_predict,
)

EMOTION_GROUPS = {
    "joy": {
        "admiration",
        "amusement",
        "approval",
        "caring",
        "gratitude",
        "joy",
        "love",
        "pride",
        "relief",
    },
    "sadness": {
        "sadness",
        "disappointment",
        "embarrassment",
        "grief",
        "remorse",
        "loneliness",
    },
    "anger": {"anger", "annoyance", "disgust", "disapproval", "frustration"},
    "fear": {"fear", "nervousness", "anxiety", "worry"},
    "surprise": {"surprise", "realization", "confusion"},
    "neutral": {"neutral", "curiosity", "desire"},
}


def map_to_coarse(label: str) -> str:
    label = (label or "neutral").lower()
    for group, items in EMOTION_GROUPS.items():
        if label in items:
            return group
    return "neutral"


def load_dataset(file_paths):
    dfs = [pd.read_csv(path) for path in file_paths]
    data = pd.concat(dfs, ignore_index=True)
    emotion_cols = data.columns.tolist()
    start_idx = emotion_cols.index("admiration")
    emotion_cols = emotion_cols[start_idx:]
    data = data[["text"] + emotion_cols].dropna(subset=["text"])

    records = []
    for row in data.itertuples():
        positives = [emotion for emotion in emotion_cols if getattr(row, emotion) == 1]
        if not positives:
            continue
        records.append({"text": getattr(row, "text"), "label": positives[0]})
    return records


def evaluate(records, output_dir: Path, sample_size: int | None = None):
    df = pd.DataFrame(records)
    if sample_size:
        df = df.sample(n=min(sample_size, len(df)), random_state=42)

    y_true = []
    preds_tf = []
    preds_lstm = []
    preds_ensemble = []

    for row in df.itertuples():
        text = row.text
        label = row.label.lower()
        y_true.append(label)

        tf_labels, _ = transformer_predict(text, top_n=1)
        preds_tf.append(tf_labels[0] if tf_labels else "neutral")

        lstm_labels, _ = lstm_predict_only(text, top_n=1)
        preds_lstm.append(lstm_labels[0] if lstm_labels else "neutral")

        ens_labels, _ = predict_emotions(text, top_n=1)
        preds_ensemble.append(ens_labels[0] if ens_labels else "neutral")

    labels_sorted = sorted(set(y_true))
    coarse_true = [map_to_coarse(label) for label in y_true]
    coarse_tf = [map_to_coarse(label) for label in preds_tf]
    coarse_lstm = [map_to_coarse(label) for label in preds_lstm]
    coarse_ens = [map_to_coarse(label) for label in preds_ensemble]

    output_dir.mkdir(parents=True, exist_ok=True)

    def save_report(name, truth, preds):
        report = classification_report(truth, preds, labels=labels_sorted, zero_division=0, output_dict=True)
        macro_f1 = f1_score(truth, preds, average="macro", zero_division=0)
        cm = confusion_matrix(truth, preds, labels=labels_sorted)
        with open(output_dir / f"{name}_classification_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        pd.DataFrame(cm, index=labels_sorted, columns=labels_sorted).to_csv(
            output_dir / f"{name}_confusion_matrix.csv"
        )
        return macro_f1

    macro_tf = save_report("transformer", y_true, preds_tf)
    macro_lstm = save_report("lstm", y_true, preds_lstm)
    macro_ens = save_report("ensemble", y_true, preds_ensemble)

    coarse_labels = sorted(EMOTION_GROUPS.keys())

    def save_coarse(name, truth, preds):
        report = classification_report(truth, preds, labels=coarse_labels, zero_division=0, output_dict=True)
        with open(output_dir / f"{name}_coarse_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    save_coarse("transformer", coarse_true, coarse_tf)
    save_coarse("lstm", coarse_true, coarse_lstm)
    save_coarse("ensemble", coarse_true, coarse_ens)

    summary = {
        "num_samples": len(y_true),
        "macro_f1_transformer": macro_tf,
        "macro_f1_lstm": macro_lstm,
        "macro_f1_ensemble": macro_ens,
        "label_distribution": Counter(y_true),
    }

    with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Evaluation complete. Summary saved to", output_dir / "summary.json")


def main():
    parser = argparse.ArgumentParser(description="Evaluate emotion models on GoEmotions dataset.")
    parser.add_argument(
        "--data-files",
        nargs="+",
        default=[
            "data/goemotions_1.csv",
            "data/goemotions_2.csv",
            "data/goemotions_3.csv",
        ],
    )
    parser.add_argument("--output-dir", type=str, default="mlops/artifacts/eval")
    parser.add_argument("--sample-size", type=int, default=2000, help="Optional subsample for quicker evaluation.")
    args = parser.parse_args()

    records = load_dataset(args.data_files)
    evaluate(records, Path(args.output_dir), sample_size=args.sample_size)


if __name__ == "__main__":
    main()

