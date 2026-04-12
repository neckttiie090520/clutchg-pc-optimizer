"""
Logger Setup
Configures logging for the ClutchG application
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from core.paths import log_dir as _default_log_dir


def setup_logging(log_level: str = "INFO", log_dir: Path = None):
    """
    Setup application logging

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ./data/logs)
    """

    # Default log directory
    if log_dir is None:
        log_dir = _default_log_dir()

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"clutchg_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("ClutchG Application Started")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
