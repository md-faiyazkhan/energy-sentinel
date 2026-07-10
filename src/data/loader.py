from pathlib import Path

import pandas as pd

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UKDALELoader:
    """
    Loads UK-DALE House 1 channel data from raw .dat files.

    Responsibilities:
    - Validate that required channel files exist
    - Read each channel into a pandas DataFrame
    - Convert Unix timestamps to datetime
    - Map channel numbers to appliance names

    Does NOT perform any preprocessing, resampling, or feature engineering.
    """

    def __init__(self) -> None:
        self.house_dir: Path = settings.RAW_DIR / settings.HOUSE_DIR_NAME
        self.channel_map: dict[int, str] = settings.CHANNEL_MAP

        # Reverse mapping for O(1) lookup in load_appliance()
        self._appliance_to_channel: dict[str, int] = {
            name: cid for cid, name in self.channel_map.items()
        }

    def _get_channel_path(self, channel_id: int) -> Path:
        """Return the file path for a given channel ID."""
        return self.house_dir / f"channel_{channel_id}.dat"

    def _validate_files(self) -> None:
        """
        Check that all required channel files exist.
        Raises FileNotFoundError if any file is missing.
        """
        missing = []
        for channel_id in self.channel_map:
            path = self._get_channel_path(channel_id)
            if not path.exists():
                missing.append(str(path))

        if missing:
            raise FileNotFoundError(
                "Missing required channel files:\n" + "\n".join(missing)
            )

        logger.info("All required channel files found.")

    def _load_channel(self, channel_id: int, appliance_name: str) -> pd.DataFrame:
        """
        Load a single channel .dat file into a DataFrame.

        UK-DALE .dat files are whitespace-separated with two columns:
        - Unix timestamp (int64)
        - Power reading in watts (float32)

        Returns a DataFrame with columns: [timestamp, power, appliance]
        """
        path = self._get_channel_path(channel_id)

        df = pd.read_csv(
            path,
            sep=r"\s+",
            header=None,
            names=["timestamp", "power"],
            dtype={"timestamp": "int64", "power": "float32"},
            engine="python",
        )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"], unit="s", utc=True, errors="raise"
        )
        df["appliance"] = appliance_name

        logger.info(
            f"Loaded channel_{channel_id} ({appliance_name}): {len(df):,} records"
        )

        return df

    def load_all(self) -> dict[str, pd.DataFrame]:
        """
        Load all required channels.

        Returns:
            dict mapping appliance name to its DataFrame.
            Example: {"Fridge": <DataFrame>, "Kettle": <DataFrame>, ...}
        """
        logger.info(f"Loading all channels from: {self.house_dir}")
        self._validate_files()

        data: dict[str, pd.DataFrame] = {}

        for channel_id, appliance_name in self.channel_map.items():
            df = self._load_channel(channel_id, appliance_name)
            data[appliance_name] = df

        logger.info(f"Successfully loaded {len(data)} channels.")
        return data

    def load_appliance(self, appliance_name: str) -> pd.DataFrame:
        """
        Load a single appliance by name.

        Args:
            appliance_name: Must match a value in CHANNEL_MAP (e.g. "Fridge")

        Returns:
            DataFrame for that appliance.

        Raises:
            ValueError if appliance_name is not in the channel map.
            FileNotFoundError if the channel file does not exist.
        """
        if appliance_name not in self._appliance_to_channel:
            valid = list(self.channel_map.values())
            raise ValueError(
                f"'{appliance_name}' not found in channel map. "
                f"Valid appliances: {valid}"
            )

        channel_id = self._appliance_to_channel[appliance_name]

        path = self._get_channel_path(channel_id)
        if not path.exists():
            raise FileNotFoundError(f"Channel file not found: {path}")

        return self._load_channel(channel_id, appliance_name)