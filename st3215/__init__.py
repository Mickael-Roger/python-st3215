# -*- coding: utf-8 -*-

"""Top-level package for st3215."""

__version__ = "IN_PROGRESS"

import logging

from .st3215 import *
from .errors import (
    ST3215Error,
    PortError,
    PacketError,
    TimeoutError,
    CommunicationError,
    ServoError,
    ValidationError,
)


def configure_logging(level=logging.WARNING, handler=None):
    """
    Configure logging for the st3215 package.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING)
        handler: Optional custom logging handler. If None, a StreamHandler is used.

    Example:
        >>> import st3215
        >>> import logging
        >>> st3215.configure_logging(level=logging.DEBUG)
    """
    logger = logging.getLogger("st3215")
    logger.setLevel(level)

    logger.handlers = []

    if handler is None:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False


configure_logging(level=logging.WARNING)
