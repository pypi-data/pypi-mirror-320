# src/nyc_records_db/config/settings.py
"""Database configuration settings for NYC Records database.

This module provides configuration management for database connections using Pydantic.
Environment variables are used to configure the database connection with the prefix NYC_RECORDS_.

Example:
    To use these settings:
    ```
    from config.settings import DatabaseSettings

    settings = DatabaseSettings()
    db_url = settings.DATABASE_URL
    ```

Environment Variables:
    NYC_RECORDS_DB_USER: Database username
    NYC_RECORDS_DB_PASS: Database password
    NYC_RECORDS_DB_HOST: Database host (default: localhost)
    NYC_RECORDS_DB_PORT: Database port (default: 5432)
    NYC_RECORDS_DB_NAME: Database name (default: nyc_records)
"""

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    DB_USER: str
    DB_PASS: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "nyc_records"

    @property
    def DATABASE_URL(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        """Pydantic configuration."""

        env_prefix = "NYC_RECORDS_"
