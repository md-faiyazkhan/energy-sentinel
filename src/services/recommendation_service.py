import pandas as pd
from src.config.settings import settings
from src.models.predictor import AnomalyPredictor
from src.utils.logger import get_logger

logger = get_logger(__name__)

ON_THRESHOLD = 5.0

APPLIANCES = [
    "Aggregate",
    "Washing Machine",
    "Dishwasher",
    "TV",
    "Kettle",
    "Fridge",
    "Microwave",
]


def generate_recommendation(
    appliance: str,
    anomaly_pct: float,
    high_risk_count: int,
    avg_power: float,
) -> str | None:
    """
    Generate a rule-based recommendation for an appliance.

    Rules:
    - anomaly_pct > 10%     : High anomaly rate warning
    - high_risk_count > 500 : Persistent high-risk anomalies
    - Fridge avg_power > 60 : Fridge running hot (above normal baseline)

    Returns a recommendation string or None if appliance looks normal.
    """
    if anomaly_pct > 10:
        return (
            f"{appliance} has shown abnormal behavior in {anomaly_pct:.1f}% of readings. "
            f"Consider inspecting the appliance for faults or unusual usage."
        )

    if high_risk_count > 500:
        return (
            f"{appliance} has recorded {high_risk_count:,} high-risk anomalies. "
            f"Persistent deviation from normal pattern detected — inspection recommended."
        )

    if appliance == "Fridge" and avg_power > 60:
        return (
            f"Fridge average power consumption ({avg_power:.1f}W) is above its normal baseline. "
            f"This may indicate a cooling issue or door seal problem."
        )

    return None


class RecommendationService:
    """
    Generates rule-based recommendations based on anomaly detection results.

    Responsibilities:
    - Analyze anomaly results per appliance
    - Apply recommendation rules
    - Return actionable insights for the dashboard
    """

    def __init__(self) -> None:
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Load feature dataset from processed parquet."""
        path = settings.PROCESSED_DIR / "house_1_features_2013.parquet"
        df = pd.read_parquet(path)
        logger.info(f"RecommendationService: loaded data, shape={df.shape}")
        return df

    def get_recommendations(self) -> list[dict]:
        """
        Generate recommendations for all appliances.

        Returns:
            List of dicts with appliance name and recommendation text.
            Only includes appliances that have actionable recommendations.
        """
        recommendations = []

        for appliance in APPLIANCES:
            try:
                predictor = AnomalyPredictor(appliance, model_name="isolation_forest")
                df_result = predictor.predict(self.data)

                total = len(df_result)
                anomaly_count = int((df_result["anomaly_label"] == -1).sum())
                anomaly_pct = round(anomaly_count / total * 100, 2)

                high_risk_count = int(
                    (df_result["anomaly_score"] <= -0.05).sum()
                )

                avg_power = round(float(self.data[appliance].mean()), 2)

                recommendation = generate_recommendation(
                    appliance, anomaly_pct, high_risk_count, avg_power
                )

                if recommendation:
                    recommendations.append({
                        "appliance": appliance,
                        "anomaly_pct": anomaly_pct,
                        "high_risk_count": high_risk_count,
                        "recommendation": recommendation,
                    })

            except Exception as e:
                logger.warning(f"Could not generate recommendation for {appliance}: {e}")

        logger.info(f"Generated {len(recommendations)} recommendations.")
        return recommendations