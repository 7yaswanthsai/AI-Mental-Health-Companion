"""
MLflow inference logging for emotion predictions, PWI, and recommendations.
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional

import mlflow
from mlops.mlflow_config import config


def log_emotion_prediction(
    text: str,
    emotion: str,
    probability: float,
    model_version: Optional[str] = None,
    subject_id: Optional[str] = None,
) -> None:
    """Log an emotion prediction to MLflow."""
    try:
        mlflow.set_tracking_uri(config.tracking_uri)
        mlflow.set_experiment(config.experiment_name)
        
        with mlflow.start_run(run_name=f"inference-{datetime.utcnow().isoformat()}", nested=True):
            mlflow.log_param("prediction_type", "emotion")
            mlflow.log_param("emotion", emotion)
            mlflow.log_param("subject_id", subject_id or "unknown")
            mlflow.log_metric("probability", float(probability))
            if model_version:
                mlflow.log_param("model_version", model_version)
            # Log text length (not the text itself for privacy)
            mlflow.log_param("text_length", len(text))
            mlflow.log_param("timestamp", datetime.utcnow().isoformat())
    except Exception as e:
        # Don't fail the main request if logging fails
        print(f"MLflow logging error: {e}")


def log_wellness_snapshot(
    subject_id: str,
    pwi: float,
    status: str,
    features: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a wellness/PWI snapshot to MLflow."""
    try:
        mlflow.set_tracking_uri(config.tracking_uri)
        mlflow.set_experiment(config.experiment_name)
        
        with mlflow.start_run(run_name=f"wellness-{subject_id}-{datetime.utcnow().isoformat()}", nested=True):
            mlflow.log_param("prediction_type", "wellness")
            mlflow.log_param("subject_id", subject_id)
            mlflow.log_metric("pwi", float(pwi))
            mlflow.log_param("status", status)
            if features:
                for key, value in features.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(f"feature_{key}", float(value))
            mlflow.log_param("timestamp", datetime.utcnow().isoformat())
    except Exception as e:
        print(f"MLflow wellness logging error: {e}")


def log_recommendation_triggered(
    emotion: str,
    wellness_status: Optional[str],
    recommendations: list,
    subject_id: Optional[str] = None,
) -> None:
    """Log when recommendations are generated."""
    try:
        mlflow.set_tracking_uri(config.tracking_uri)
        mlflow.set_experiment(config.experiment_name)
        
        with mlflow.start_run(run_name=f"recommendations-{datetime.utcnow().isoformat()}", nested=True):
            mlflow.log_param("prediction_type", "recommendations")
            mlflow.log_param("emotion", emotion)
            mlflow.log_param("wellness_status", wellness_status or "unknown")
            mlflow.log_param("subject_id", subject_id or "unknown")
            mlflow.log_metric("num_recommendations", len(recommendations))
            mlflow.log_param("timestamp", datetime.utcnow().isoformat())
    except Exception as e:
        print(f"MLflow recommendation logging error: {e}")


def log_chat_interaction(
    subject_id: str,
    emotion: str,
    pwi: Optional[float],
    num_recommendations: int,
    escalate: bool = False,
) -> None:
    """Log a complete chat interaction summary."""
    try:
        mlflow.set_tracking_uri(config.tracking_uri)
        mlflow.set_experiment(config.experiment_name)
        
        with mlflow.start_run(run_name=f"chat-{subject_id}-{datetime.utcnow().isoformat()}", nested=True):
            mlflow.log_param("prediction_type", "chat_interaction")
            mlflow.log_param("subject_id", subject_id)
            mlflow.log_param("emotion", emotion)
            if pwi is not None:
                mlflow.log_metric("pwi", float(pwi))
            mlflow.log_metric("num_recommendations", num_recommendations)
            mlflow.log_param("escalate", str(escalate))
            mlflow.log_param("timestamp", datetime.utcnow().isoformat())
    except Exception as e:
        print(f"MLflow chat logging error: {e}")

