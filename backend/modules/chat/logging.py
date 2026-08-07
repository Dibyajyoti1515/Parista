"""Logging infrastructure for the Parista backend."""

import logging
from typing import Any

import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)


def get_logger(name: str = "parista") -> Any:
    """Return a structured logger for the given module name."""
    return structlog.get_logger(name)


logger = get_logger("parista")