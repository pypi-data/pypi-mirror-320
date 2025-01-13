# packages/src/nyc_records_db/migrations/__init__.py
"""Database migrations package for NYC Records Database.

This package contains Alembic migrations for managing database schema changes:
- Migration scripts in versions/
- Migration environment configuration
- Utility functions for migration management

Usage:
    alembic upgrade head  # Run all migrations
    alembic revision -m "description"  # Create new migration
    alembic downgrade -1  # Rollback last migration
"""

from alembic import context

__all__ = ["context"]
