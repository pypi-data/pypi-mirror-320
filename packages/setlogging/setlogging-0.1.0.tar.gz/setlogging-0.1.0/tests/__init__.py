# src/setlogging/__init__.py

from setlogging.logger import (
    TimezoneFormatter,
    setup_logging,
    get_logger,
)

__version__ = "0.1.0"
__author__ = "Jie Yan"
__email__ = "kiki3890528@gmail.com"

__all__ = [
    "TimezoneFormatter",
    "setup_logging",
    "get_logger",
]
