# src/nyc_records_db/models/tables/nyc_asset_details.py
"""Define NYC Asset Details model for historical records and documents.

This module implements the SQLAlchemy ORM model for the nyc_asset_details table.
It stores information about historical NYC records including documents, photos,
and other archival materials.

Table Schema:
    - Primary Key: id (serial)
    - Unique Constraint: identifier
    - Timestamp: last_scraped (auto-updated)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class NYCAssetDetails(Base):
    """NYC Asset Details model for historical records and documents."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    borough: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    block: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lot: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    collection: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    object_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_scraped: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, server_default="CURRENT_TIMESTAMP"
    )
    raw_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    boro_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    def __repr__(self) -> str:
        """Return string representation of the asset details."""
        return f"<NYCAssetDetails(id={self.id}, identifier='{self.identifier}')>"
