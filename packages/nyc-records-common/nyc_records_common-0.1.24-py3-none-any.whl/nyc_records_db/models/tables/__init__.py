# packages/src/nyc_records_db/models/tables/__init__.py
"""Database table models for NYC Records Database.

This package contains SQLAlchemy ORM table definitions:
- NYC Asset Details: Historical records and documents
- Additional tables will be added as needed

Table Structure:
    nyc_asset_details
    - Primary key: id (serial)
    - Unique constraint: identifier
    - Timestamps: last_scraped
"""

from .nyc_asset_details import NYCAssetDetails

__all__ = ["NYCAssetDetails"]
