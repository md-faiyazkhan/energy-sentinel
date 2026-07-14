import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnomalyPredictor:
    """
    Loads a trained model bundle and runs anomaly predictions.

    Responsibilities:
    - Load saved model bundle from artifacts/
    - Scale input features using saved scaler
    - Run predictions using selected model
    - Return anomaly labels and scores

    Does NOT perform feature engineering or training.
    """

    def __init__(self, appliance: str, model_name: str = "isolation_forest") -> None:
        """
        Args:
            appliance  : Appliance name (e.g. "Fridge")
            model_name : One of isolation_forest, lof, ocsvm
        """
        self.appliance = appliance
        self.model_name = model_name
        self.model_bundle = self._load_bundle()

    def _load_bundle(self) -> dict:
        """Load model bundle from artifacts/."""
        appliance_clean = self.appliance.replace(" ", "_").lower()
        path = settings.ARTIFACTS_DIR / f"{appliance_clean}_models.joblib"

        if not path.exists():
            raise FileNotFoundError(
                f"Model bundle not found for {self.appliance}: {path}"
            )

        bundle = joblib.load(path)
        logger.info(f"Loaded model bundle for {self.appliance} ({self.model_name})")
        return bundle

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run anomaly detection on input DataFrame.

        Args:
            df: Feature DataFrame (must contain required feature columns)

        Returns:
            DataFrame with two new columns:
            - anomaly_label : 1 = normal, -1 = anomaly
            - anomaly_score : raw decision score (lower = more anomalous)
        """
        feature_cols = self.model_bundle["feature_cols"]
        scaler = self.model_bundle["scaler"]
        model = self.model_bundle[self.model_name]

        X = df[feature_cols].values
        X_scaled = scaler.transform(X)

        result = df.copy()
        result["anomaly_label"] = model.predict(X_scaled)
        result["anomaly_score"] = model.decision_function(X_scaled)

        anomaly_count = (result["anomaly_label"] == -1).sum()
        logger.info(
            f"{self.appliance} ({self.model_name}): "
            f"{anomaly_count:,} anomalies detected out of {len(result):,} records"
        )

        return result