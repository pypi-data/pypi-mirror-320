# src/nyc_records_common/__init__.py
"""NYC Records Common Package.

Provides shared utilities for NYC Records projects.
"""

from .cloud.secrets import load_secret
from .utils.fs import ensure_dir_exists
from .utils.time import calculate_duration, format_timestamp

__all__ = (
    "ensure_dir_exists",
    "load_secret",
    "calculate_duration",
    "format_timestamp",
)
