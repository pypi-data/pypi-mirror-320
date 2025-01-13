# packages/src/nyc_records_db/models/__init__.py
"""Database models package for NYC Records Database.

This package contains SQLAlchemy ORM models:
- Base model configuration
- NYC Asset Details model
- Table definitions and relationships

Usage:
    from nyc_records_db.models import NYCAssetDetails

    asset = NYCAssetDetails(
        identifier="123",
        url="http://example.com"
    )
"""

from .base import Base
from .tables.nyc_asset_details import NYCAssetDetails

__all__ = ["Base", "NYCAssetDetails"]
