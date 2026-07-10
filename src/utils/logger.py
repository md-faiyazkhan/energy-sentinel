import logging
import sys
from src.config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.

    Usage:
        from src.utils.logger import get_logger
        logger = get_logger(__name__)

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(settings.LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger