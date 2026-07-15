import pandas as pd
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

APPLIANCES = [
    "Washing Machine",
    "Dishwasher",
    "TV",
    "Kettle",
    "Fridge",
    "Microwave",
]


class AnalyticsService:
    """
    Provides usage pattern analytics per appliance.

    Responsibilities:
    - Hourly usage patterns
    - Weekday vs weekend comparison
    - Peak usage hours
    - Daily activity rates
    """

    def __init__(self) -> None:
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Load cleaned dataset from processed parquet."""
        path = settings.PROCESSED_DIR / "house_1_cleaned_2013.parquet"
        df = pd.read_parquet(path)
        logger.info(f"AnalyticsService: loaded data, shape={df.shape}")
        return df

    def get_hourly_pattern(self, appliance: str) -> list[dict]:
        """
        Returns average power consumption per hour of day for an appliance.
        """
        df = self.data.copy()
        df["hour"] = df.index.hour

        hourly = df.groupby("hour")[appliance].mean().round(2)

        return [
            {"hour": int(hour), "avg_power_watts": float(val)}
            for hour, val in hourly.items()
        ]

    def get_weekday_vs_weekend(self, appliance: str) -> dict:
        """
        Returns average hourly power for weekday vs weekend.
        """
        df = self.data.copy()
        df["hour"] = df.index.hour
        df["is_weekend"] = df.index.dayofweek >= 5

        weekday = df[df["is_weekend"] == False].groupby("hour")[appliance].mean().round(2)
        weekend = df[df["is_weekend"] == True].groupby("hour")[appliance].mean().round(2)

        return {
            "weekday": [
                {"hour": int(h), "avg_power_watts": float(v)}
                for h, v in weekday.items()
            ],
            "weekend": [
                {"hour": int(h), "avg_power_watts": float(v)}
                for h, v in weekend.items()
            ],
        }

    def get_peak_hour(self, appliance: str) -> dict:
        """
        Returns the peak usage hour for an appliance.
        """
        df = self.data.copy()
        df["hour"] = df.index.hour

        hourly = df.groupby("hour")[appliance].mean()
        peak_hour = int(hourly.idxmax())
        peak_power = round(float(hourly.max()), 2)

        return {
            "appliance": appliance,
            "peak_hour": peak_hour,
            "peak_avg_power_watts": peak_power,
        }

    def get_daily_activity_rate(self, appliance: str) -> list[dict]:
        """
        Returns daily activity rate (% time ON) for an appliance.
        """
        ON_THRESHOLD = 5.0

        daily_rate = (
            (self.data[appliance] > ON_THRESHOLD)
            .resample("D")
            .mean()
            .mul(100)
            .round(2)
        )

        return [
            {"date": str(ts.date()), "activity_rate_pct": float(val)}
            for ts, val in daily_rate.items()
        ]