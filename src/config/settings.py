from pathlib import Path
from pydantic_settings import BaseSettings


# Project root — two levels up from this file (src/config/settings.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Paths
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
    PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"
    ARTIFACTS_DIR: Path = PROJECT_ROOT / "artifacts"

    # UK-DALE House 1
    HOUSE_ID: int = 1
    HOUSE_DIR_NAME: str = "house_1"

    # Channel to appliance mapping — only channels we care about
    CHANNEL_MAP: dict[int, str] = {
        1: "Aggregate",
        5: "Washing Machine",
        6: "Dishwasher",
        7: "TV",
        10: "Kettle",
        12: "Fridge",
        13: "Microwave",
    }

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()