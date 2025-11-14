import argparse
from pathlib import Path

import mlflow
import mlflow.tensorflow
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import tensorflow as tf
from matplotlib import pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

from mlops.mlflow_config import config


def load_dataset(files):
    dfs = [pd.read_csv(path) for path in files]
    data = pd.concat(dfs, ignore_index=True)
    emotion_cols = data.columns.tolist()
    start_idx = emotion_cols.index("admiration")
    emotion_cols = emotion_cols[start_idx:]
    data = data[["text"] + emotion_cols].dropna(subset=["text"])
    labels = data[emotion_cols].values.astype("float32")
    return data["text"].tolist(), labels, emotion_cols


def tokenize_texts(texts, num_words=10000, max_len=50):
    tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=num_words, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded = tf.keras.preprocessing.sequence.pad_sequences(sequences, maxlen=max_len, padding="post", truncating="post")
    return tokenizer, padded


def build_model(vocab_size, sequence_length, num_classes):
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=128, input_length=sequence_length),
            tf.keras.layers.LSTM(64),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(num_classes, activation="sigmoid"),
        ]
    )
    model.compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=["accuracy"],
    )
    return model


def plot_confusion_matrix(y_true, y_pred, labels, output_path):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=False, cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return cm


def main():
    parser = argparse.ArgumentParser(description="Train emotion model with MLflow tracking.")
    parser.add_argument(
        "--data-files",
        nargs="+",
        default=[
            "data/goemotions_1.csv",
            "data/goemotions_2.csv",
            "data/goemotions_3.csv",
        ],
        help="Paths to GoEmotions CSV files.",
    )
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-len", type=int, default=50)
    parser.add_argument("--num-words", type=int, default=10000)
    parser.add_argument("--output-dir", type=str, default="backend/models")
    parser.add_argument("--artifacts-dir", type=str, default="mlops/artifacts")
    args = parser.parse_args()

    texts, labels, emotion_cols = load_dataset(args.data_files)
    mlb = MultiLabelBinarizer()
    mlb.fit([emotion_cols])
    tokenizer, padded = tokenize_texts(texts, num_words=args.num_words, max_len=args.max_len)

    X_train, X_test, y_train, y_test = train_test_split(padded, labels, test_size=0.1, random_state=42)

    model = build_model(args.num_words, args.max_len, len(emotion_cols))

    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mlflow.set_tracking_uri(config.tracking_uri)
    mlflow.set_experiment(config.experiment_name)
    mlflow.tensorflow.autolog(every_n_iter=0, log_models=False)

    with mlflow.start_run():
        mlflow.log_params(
            {
                "epochs": args.epochs,
                "batch_size": args.batch_size,
                "max_len": args.max_len,
                "num_words": args.num_words,
                "num_classes": len(emotion_cols),
            }
        )

        history = model.fit(
            X_train,
            y_train,
            epochs=args.epochs,
            batch_size=args.batch_size,
            validation_split=0.1,
            verbose=1,
        )

        loss, acc = model.evaluate(X_test, y_test, verbose=0)
        y_pred_probs = model.predict(X_test)
        y_pred_labels = (y_pred_probs >= 0.5).astype(int)

        # For macro metrics treat multi-label as sets; use flattened approach
        macro_f1 = f1_score(y_test.flatten(), y_pred_labels.flatten(), average="macro", zero_division=0)
        acc_score = accuracy_score(y_test.flatten(), y_pred_labels.flatten())

        mlflow.log_metric("test_loss", float(loss))
        mlflow.log_metric("test_accuracy", float(acc))
        mlflow.log_metric("flat_accuracy", float(acc_score))
        mlflow.log_metric("macro_f1", float(macro_f1))

        # Confusion matrix for primary label approximation
        y_true_single = np.argmax(y_test, axis=1)
        y_pred_single = np.argmax(y_pred_probs, axis=1)
        cm_path = artifacts_dir / "confusion_matrix.png"
        plot_confusion_matrix(y_true_single, y_pred_single, list(range(len(emotion_cols))), cm_path)
        mlflow.log_artifact(str(cm_path))

        # Save model + tokenizer
        model_path = output_dir / "emotion_lstm_model.h5"
        model.save(model_path)
        tokenizer_path = output_dir / "tokenizer.pkl"

        with open(tokenizer_path, "wb") as f:
            pickle.dump(tokenizer, f)

        # Save label binarizer for downstream use
        label_path = output_dir / "mlb.pkl"
        with open(label_path, "wb") as f:
            pickle.dump(mlb, f)

        mlflow.log_artifact(str(model_path))
        mlflow.log_artifact(str(tokenizer_path))
        mlflow.log_artifact(str(label_path))

        summary_path = artifacts_dir / "classification_report.txt"
        report = classification_report(
            y_true_single,
            y_pred_single,
            labels=list(range(len(emotion_cols))),
            target_names=emotion_cols,
            zero_division=0,
        )
        summary_path.write_text(report)
        mlflow.log_artifact(str(summary_path))

    print("Training complete. Model saved to", model_path)


if __name__ == "__main__":
    main()

