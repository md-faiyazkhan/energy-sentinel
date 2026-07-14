import pandas as pd
from src.config.settings import settings
from src.models.predictor import AnomalyPredictor
from src.utils.logger import get_logger

logger = get_logger(__name__)

APPLIANCES = [
    "Aggregate",
    "Washing Machine",
    "Dishwasher",
    "TV",
    "Kettle",
    "Fridge",
    "Microwave",
]


def get_risk_level(anomaly_score: float) -> str:
    """
    Convert anomaly score to risk level.

    Isolation Forest scores:
    - Positive score = more normal
    - Negative score = more anomalous

    Risk tiers:
    - score > 0.0        : Low
    - -0.05 < score <= 0 : Medium
    - score <= -0.05     : High
    """
    if anomaly_score > 0.0:
        return "Low"
    elif anomaly_score > -0.05:
        return "Medium"
    else:
        return "High"


class HealthService:
    """
    Runs anomaly detection and returns appliance health status.

    Responsibilities:
    - Load feature dataset
    - Run Isolation Forest predictions per appliance
    - Assign risk levels based on anomaly scores
    - Return appliance health summaries
    """

    def __init__(self) -> None:
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Load feature dataset from processed parquet."""
        path = settings.PROCESSED_DIR / "house_1_features_2013.parquet"
        df = pd.read_parquet(path)
        logger.info(f"HealthService: loaded data, shape={df.shape}")
        return df

    def get_appliance_health(self, appliance: str) -> dict:
        """
        Returns anomaly detection results and health status for one appliance.

        Args:
            appliance: Appliance name (e.g. "Fridge")

        Returns:
            dict with anomaly count, risk distribution, and recent anomalies
        """
        predictor = AnomalyPredictor(appliance, model_name="isolation_forest")
        df_result = predictor.predict(self.data)

        df_result["risk_level"] = df_result["anomaly_score"].apply(get_risk_level)

        total = len(df_result)
        anomaly_count = int((df_result["anomaly_label"] == -1).sum())
        anomaly_pct = round(anomaly_count / total * 100, 2)

        risk_counts = df_result["risk_level"].value_counts().to_dict()

        # Most recent 10 anomalies
        recent_anomalies = (
            df_result[df_result["anomaly_label"] == -1]
            .tail(10)[["anomaly_score", "risk_level", appliance]]
            .reset_index()
            .rename(columns={"timestamp": "timestamp", appliance: "power_watts"})
            .to_dict(orient="records")
        )

        return {
            "appliance": appliance,
            "total_records": total,
            "anomaly_count": anomaly_count,
            "anomaly_pct": anomaly_pct,
            "risk_distribution": risk_counts,
            "recent_anomalies": recent_anomalies,
        }

    def get_all_health_summary(self) -> list[dict]:
        """
        Returns a brief health summary for all appliances.
        """
        summary = []

        for appliance in APPLIANCES:
            try:
                predictor = AnomalyPredictor(appliance, model_name="isolation_forest")
                df_result = predictor.predict(self.data)
                df_result["risk_level"] = df_result["anomaly_score"].apply(get_risk_level)

                anomaly_count = int((df_result["anomaly_label"] == -1).sum())
                high_risk = int((df_result["risk_level"] == "High").sum())

                overall_status = "Critical" if high_risk > 100 else "Warning" if anomaly_count > 1000 else "Normal"

                summary.append({
                    "appliance": appliance,
                    "anomaly_count": anomaly_count,
                    "high_risk_count": high_risk,
                    "overall_status": overall_status,
                })

            except Exception as e:
                logger.warning(f"Could not get health for {appliance}: {e}")
                summary.append({
                    "appliance": appliance,
                    "anomaly_count": 0,
                    "high_risk_count": 0,
                    "overall_status": "Unknown",
                })

        return summary