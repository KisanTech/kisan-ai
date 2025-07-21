"""
Structured logging setup for Project Kisan using structlog
"""

import logging
import os
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import structlog

from app.core.config import settings


# Configure logging on first import
def _configure_logging():
    """Configure logging settings - called once during import"""
    # Ensure logs directory exists only when needed
    os.makedirs("logs", exist_ok=True)

    # Set the root logger level based on DEBUG setting
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(level=log_level)


_configure_logging()

# Configure structlog
structlog.configure(
    processors=[
        # Filter by log level
        structlog.stdlib.filter_by_level,
        # Add log level to log entry
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="ISO"),
        # Add JSON formatting for file output, colored console for dev
        structlog.dev.ConsoleRenderer(colors=True)
        if settings.DEBUG
        else structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Get logger instance
logger = structlog.get_logger("project-kisan")


def log_latency(operation_name: str = None):
    """
    Decorator to log API call latency with structured logging

    Usage:
        @log_latency("fetch_market_prices")
        async def get_prices():
            ...

    Logs:
        - operation_start: When function begins
        - operation_complete: When function succeeds (with latency)
        - operation_failed: When function fails (with latency and error)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            operation = operation_name or func.__name__

            logger.info("Operation started", operation=operation, function=func.__name__)

            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000

                logger.info(
                    "Operation completed successfully",
                    operation=operation,
                    function=func.__name__,
                    latency_ms=round(latency_ms, 2),
                    status="success",
                )
                return result

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Operation failed",
                    operation=operation,
                    function=func.__name__,
                    latency_ms=round(latency_ms, 2),
                    status="failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        return wrapper

    return decorator
