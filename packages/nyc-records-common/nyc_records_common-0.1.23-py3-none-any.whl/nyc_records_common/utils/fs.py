# src/nyc_records_common/utils/fs.py
"""Filesystem utility functions."""
from pathlib import Path
from typing import Union


def ensure_dir_exists(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't.

    Args:
        path: Directory path to ensure exists

    Returns:
        Path: Path object of created/existing directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
