# packages/src/nyc_records_db/config/__init__.py
"""Configuration package for NYC Records Database.

Provides:
- Database connection settings
- Environment configuration
- Application settings management
"""

from .settings import DatabaseSettings

__all__ = ["DatabaseSettings"]
