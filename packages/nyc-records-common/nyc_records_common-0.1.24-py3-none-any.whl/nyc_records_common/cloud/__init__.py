# src/nyc_records_common/cloud/__init__.py
"""Cloud integration utilities.

Provides tools for interacting with Google Cloud Platform services:
- Secret Manager access
- Authentication handling
"""

from .secrets import load_secret

__all__ = ["load_secret"]
