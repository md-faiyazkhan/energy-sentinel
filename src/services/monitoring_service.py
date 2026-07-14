import pandas as pd
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MonitoringService:
    """
    Provides household energy monitoring summaries.

    Responsibilities:
    - Total energy consumption
    - Per-appliance energy breakdown
    - Daily and monthly consumption trends
    """

    def __init__(self) -> None:
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Load cleaned dataset from processed parquet."""
        path = settings.PROCESSED_DIR / "house_1_cleaned_2013.parquet"
        df = pd.read_parquet(path)
        logger.info(f"MonitoringService: loaded data, shape={df.shape}")
        return df

    def get_summary(self) -> dict:
        """
        Returns high-level energy summary for the dashboard home page.
        """
        df = self.data

        total_energy_kwh = round(df["Aggregate"].sum() / 60 / 1000, 2)
        avg_daily_kwh = round(total_energy_kwh / 365, 2)
        peak_power_watts = round(df["Aggregate"].max(), 2)
        avg_power_watts = round(df["Aggregate"].mean(), 2)

        return {
            "total_energy_kwh": total_energy_kwh,
            "avg_daily_kwh": avg_daily_kwh,
            "peak_power_watts": peak_power_watts,
            "avg_power_watts": avg_power_watts,
            "num_appliances": len(df.columns),
            "date_range": {
                "start": str(df.index.min().date()),
                "end": str(df.index.max().date()),
            },
        }

    def get_monthly_trend(self) -> list[dict]:
        """
        Returns monthly average power consumption for Aggregate.
        """
        monthly = self.data["Aggregate"].resample("ME").mean().round(2)

        return [
            {"month": str(ts.date()), "avg_power_watts": val}
            for ts, val in monthly.items()
        ]

    def get_appliance_energy_breakdown(self) -> list[dict]:
        """
        Returns total energy consumed per appliance in kWh.
        Excludes Aggregate.
        """
        df = self.data.drop(columns=["Aggregate"])

        breakdown = (df.sum() / 60 / 1000).round(2)

        return [
            {"appliance": appliance, "total_energy_kwh": float(value)}
            for appliance, value in breakdown.items()
        ]