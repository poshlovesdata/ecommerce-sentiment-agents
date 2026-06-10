"""Loguru helpers used by CLI scripts and the Streamlit app."""

import sys
from pathlib import Path

from loguru import logger


def configure_logging(
    *,
    level: str = "INFO",
    log_file: Path | None = None,
    rotation: str = "10 MB",
    retention: str = "14 days",
) -> None:
    """Configure Loguru for readable local and production logs."""

    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>",
    )

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            enqueue=True,
            serialize=True,
        )
