"""Time utility functions for formatting and calculations."""

from datetime import datetime
from typing import Union

import humanize


def format_timestamp(timestamp: Union[datetime, int, float, None]) -> str:
    """Format timestamp to consistent string representation.

    Args:
        timestamp: Input timestamp as datetime, unix timestamp, or None

    Returns:
        str: Formatted date string in "YYYY-MM-DD HH:MM:S" format,
             returns empty string for None input
    """
    if timestamp is None:
        return ""

    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(timestamp, datetime):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")
    except (ValueError, TypeError, OSError):  # Removed unused 'e' variable
        return str(timestamp)


def calculate_duration(start_time: datetime, completion_time: datetime) -> str:
    """Calculate human-readable duration between timestamps.

    Args:
        start_time: Start datetime
        completion_time: End datetime

    Returns:
        str: Human readable duration (e.g. "5 minutes", "2 hours 30 minutes")
    """
    if start_time is None:
        raise TypeError("Start time cannot be None")
    if completion_time is None:
        raise TypeError("End time cannot be None")

    if completion_time < start_time:
        raise ValueError("End time must be after start time")

    duration = completion_time - start_time
    # Remove "and" from humanize output
    return humanize.precisedelta(duration, minimum_unit="seconds", format="%d").replace(" and ", " ")
