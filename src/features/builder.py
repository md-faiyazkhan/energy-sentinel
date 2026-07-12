import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Appliance ON threshold
ON_THRESHOLD = 5.0

# Rolling window — 1 hour = 60 minutes
ROLLING_WINDOW = 60


class FeatureBuilder:
    """
    Builds features for anomaly detection from cleaned appliance data.

    Responsibilities:
    - Time-based features (hour, day, weekend, month)
    - Rolling statistics (mean, std, max, min)
    - Appliance-specific features (daily energy, activity rate, cycles)

    Does NOT perform cleaning or model training.
    """

    def __init__(
        self,
        rolling_window: int = ROLLING_WINDOW,
        on_threshold: float = ON_THRESHOLD,
    ) -> None:
        self.rolling_window = rolling_window
        self.on_threshold = on_threshold

    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time-based features from the DatetimeIndex.
        """
        df = df.copy()

        df["hour"] = df.index.hour
        df["day_of_week"] = df.index.dayofweek
        df["is_weekend"] = (df.index.dayofweek >= 5).astype(int)
        df["month"] = df.index.month

        logger.info("Time features added: hour, day_of_week, is_weekend, month")
        return df

    def add_rolling_features(
        self, df: pd.DataFrame, appliance: str
    ) -> pd.DataFrame:
        """
        Add rolling statistics for a single appliance column.

        Window: 60 minutes (1 hour)
        """
        df = df.copy()

        rolling = df[appliance].rolling(window=self.rolling_window, min_periods=1)

        df[f"{appliance}_rolling_mean"] = rolling.mean()
        df[f"{appliance}_rolling_std"] = rolling.std().fillna(0)
        df[f"{appliance}_rolling_max"] = rolling.max()
        df[f"{appliance}_rolling_min"] = rolling.min()

        logger.info(f"{appliance}: rolling features added (window={self.rolling_window}min)")
        return df

    def add_daily_features(
        self, df: pd.DataFrame, appliance: str
    ) -> pd.DataFrame:
        """
        Add daily aggregated features for a single appliance.

        - daily_energy_kwh : total energy consumed per day
        - daily_activity_rate : % time ON per day
        - daily_cycles : number of ON/OFF transitions per day
        """
        df = df.copy()

        # Daily energy — power (W) * 1 minute / 60 = Wh, divide by 1000 = kWh
        daily_energy = (
            df[appliance]
            .resample("D")
            .sum() / 60 / 1000
        )

        # Daily activity rate — % time ON
        daily_activity = (
            (df[appliance] > self.on_threshold)
            .resample("D")
            .mean() * 100
        )

        # Daily cycles — count ON/OFF transitions
        is_on = (df[appliance] > self.on_threshold).astype(int)
        transitions = is_on.diff().abs()
        daily_cycles = transitions.resample("D").sum() / 2

        # Map daily values back to minute-level index
        df[f"{appliance}_daily_energy_kwh"] = df.index.normalize().map(
            daily_energy
        )
        df[f"{appliance}_daily_activity_rate"] = df.index.normalize().map(
            daily_activity
        )
        df[f"{appliance}_daily_cycles"] = df.index.normalize().map(
            daily_cycles
        )

        logger.info(f"{appliance}: daily features added (energy, activity rate, cycles)")
        return df

    def build(
        self, df: pd.DataFrame, appliances: list[str]
    ) -> pd.DataFrame:
        """
        Full feature engineering pipeline.

        Steps:
        1. Add time features
        2. Add rolling features per appliance
        3. Add daily features per appliance

        Args:
            df       : Cleaned combined DataFrame
            appliances: List of appliance column names to engineer features for

        Returns:
            DataFrame with all features added
        """
        logger.info("Starting feature engineering pipeline...")

        df = self.add_time_features(df)

        for appliance in appliances:
            if appliance not in df.columns:
                logger.warning(f"{appliance} not found in DataFrame, skipping.")
                continue
            df = self.add_rolling_features(df, appliance)
            df = self.add_daily_features(df, appliance)

        logger.info(
            f"Feature engineering complete. Total columns: {len(df.columns)}"
        )
        return df