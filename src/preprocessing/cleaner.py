import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Appliances jo continuous hain — gaps ffill se bharo
CONTINUOUS_APPLIANCES = ["Aggregate", "Fridge"]

# Appliances jo sparse hain — gaps 0 se bharo
SPARSE_APPLIANCES = ["Washing Machine", "Dishwasher", "TV", "Kettle", "Microwave"]

# 5W se kam ko OFF (0) treat karo
ON_THRESHOLD = 5.0


class DataCleaner:
    """
    Cleans and preprocesses resampled UK-DALE data.

    Responsibilities:
    - Fill missing values appropriately per appliance type
    - Apply ON/OFF threshold to remove sensor baseline noise
    - Validate cleaned data

    Does NOT perform feature engineering.
    """

    def __init__(self, threshold: float = ON_THRESHOLD) -> None:
        self.threshold = threshold

    def fill_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values per appliance type.

        Continuous appliances (Fridge, Aggregate):
            Forward fill — they are always running, gaps are sensor dropouts.

        Sparse appliances (Kettle, Microwave etc.):
            Fill with 0 — when no reading, appliance was OFF.
        """
        df = df.copy()

        for appliance in CONTINUOUS_APPLIANCES:
            if appliance in df.columns:
                before = df[appliance].isnull().sum()
                df[appliance] = df[appliance].ffill()
                after = df[appliance].isnull().sum()
                logger.info(
                    f"{appliance}: filled {before - after:,} missing values with ffill"
                )

        for appliance in SPARSE_APPLIANCES:
            if appliance in df.columns:
                before = df[appliance].isnull().sum()
                df[appliance] = df[appliance].fillna(0.0)
                after = df[appliance].isnull().sum()
                logger.info(
                    f"{appliance}: filled {before - after:,} missing values with 0"
                )

        return df

    def apply_threshold(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Set readings below threshold to 0.

        Removes 1W sensor baseline noise present in UK-DALE data.
        Only applied to appliance columns, not Aggregate.
        """
        df = df.copy()

        appliance_cols = [col for col in df.columns if col != "Aggregate"]

        for appliance in appliance_cols:
            if appliance in df.columns:
                below = (df[appliance] < self.threshold) & (df[appliance] > 0)
                df.loc[below, appliance] = 0.0
                logger.info(
                    f"{appliance}: set {below.sum():,} below-threshold readings to 0"
                )

        return df

    def validate(self, df: pd.DataFrame) -> None:
        """
        Basic validation after cleaning.
        Raises ValueError if critical issues found.
        """
        # Check for remaining nulls
        remaining_nulls = df.isnull().sum()
        if remaining_nulls.any():
            logger.warning(f"Remaining nulls after cleaning:\n{remaining_nulls}")

        # Check for negative values
        negative = (df < 0).sum()
        if negative.any():
            raise ValueError(f"Negative power values found:\n{negative}")

        logger.info("Validation passed — no critical issues found.")

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Full cleaning pipeline.

        Steps:
        1. Fill missing values
        2. Apply ON/OFF threshold
        3. Validate

        Args:
            df: Resampled combined DataFrame from EDA

        Returns:
            Cleaned DataFrame ready for feature engineering
        """
        logger.info("Starting data cleaning pipeline...")

        df = self.fill_missing(df)
        df = self.apply_threshold(df)
        self.validate(df)

        logger.info("Data cleaning complete.")
        return df