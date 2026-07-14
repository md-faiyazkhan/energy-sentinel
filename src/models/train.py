import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Features used for training
FEATURE_COLS = [
    "hour",
    "day_of_week",
    "is_weekend",
    "month",
]

APPLIANCE_FEATURE_SUFFIXES = [
    "_rolling_mean",
    "_rolling_std",
    "_rolling_max",
    "_rolling_min",
    "_daily_energy_kwh",
    "_daily_activity_rate",
    "_daily_cycles",
]

# Sample size for LOF and OCSVM comparison
COMPARISON_SAMPLE_SIZE = 10000


def get_appliance_features(appliance: str) -> list[str]:
    """
    Returns full feature column list for a given appliance.
    Combines time features + appliance-specific features.
    """
    appliance_cols = [f"{appliance}{suffix}" for suffix in APPLIANCE_FEATURE_SUFFIXES]
    return FEATURE_COLS + appliance_cols


def train_isolation_forest(X: np.ndarray, contamination: float = 0.05) -> IsolationForest:
    """
    Train Isolation Forest on full dataset.
    Primary model for production use.
    """
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)
    return model


def train_lof(X: np.ndarray, contamination: float = 0.05) -> LocalOutlierFactor:
    """
    Train LOF on a small sample for comparison only.
    Not used in production.
    """
    model = LocalOutlierFactor(
        n_neighbors=20,
        contamination=contamination,
        novelty=True,
        n_jobs=-1,
    )
    model.fit(X)
    return model


def train_ocsvm(X: np.ndarray) -> OneClassSVM:
    """
    Train One-Class SVM on a small sample for comparison only.
    Not used in production.
    """
    model = OneClassSVM(
        kernel="rbf",
        nu=0.05,
        gamma="scale",
    )
    model.fit(X)
    return model


def train_all_models(
    df: pd.DataFrame,
    appliance: str,
    contamination: float = 0.05,
) -> dict:
    """
    Train all 3 models for a single appliance.

    - Isolation Forest: trained on full dataset
    - LOF + OCSVM: trained on sample of 10,000 rows for comparison only

    Args:
        df           : Feature DataFrame
        appliance    : Appliance name (e.g. "Fridge")
        contamination: Expected proportion of anomalies

    Returns:
        dict with trained models, scaler, and feature columns
    """
    logger.info(f"Training models for: {appliance}")

    feature_cols = get_appliance_features(appliance)
    X_full = df[feature_cols].values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_full)

    # Primary model — full data
    logger.info(f"{appliance}: training Isolation Forest on {len(X_full):,} rows...")
    iso_forest = train_isolation_forest(X_scaled, contamination)

    # Comparison models — sample only
    sample_idx = np.random.choice(len(X_scaled), size=COMPARISON_SAMPLE_SIZE, replace=False)
    X_sample = X_scaled[sample_idx]

    logger.info(f"{appliance}: training LOF on {COMPARISON_SAMPLE_SIZE:,} row sample...")
    lof = train_lof(X_sample, contamination)

    logger.info(f"{appliance}: training One-Class SVM on {COMPARISON_SAMPLE_SIZE:,} row sample...")
    ocsvm = train_ocsvm(X_sample)

    logger.info(f"{appliance}: all models trained successfully")

    return {
        "isolation_forest": iso_forest,
        "lof": lof,
        "ocsvm": ocsvm,
        "scaler": scaler,
        "feature_cols": feature_cols,
        "appliance": appliance,
    }


def save_model(model_dict: dict, appliance: str) -> Path:
    """
    Save trained model bundle to artifacts/.

    Args:
        model_dict: Dict containing models and scaler
        appliance : Appliance name

    Returns:
        Path where model was saved
    """
    appliance_clean = appliance.replace(" ", "_").lower()
    output_path = settings.ARTIFACTS_DIR / f"{appliance_clean}_models.joblib"

    joblib.dump(model_dict, output_path)
    logger.info(f"Model saved: {output_path}")

    return output_path