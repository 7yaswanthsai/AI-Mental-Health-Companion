from dataclasses import dataclass
import os


@dataclass
class MLflowConfig:
    tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "file:mlruns")
    experiment_name: str = os.getenv("MLFLOW_EXPERIMENT", "emotion-model")


config = MLflowConfig()

