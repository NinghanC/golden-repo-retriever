from __future__ import annotations

import logging

from .config import settings


def configure_logging(log_level: str | None = None) -> None:
    logging.basicConfig(
        level=(log_level or settings.log_level).upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger
