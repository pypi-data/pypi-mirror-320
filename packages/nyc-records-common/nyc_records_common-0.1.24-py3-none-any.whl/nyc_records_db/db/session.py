# src/nyc_records_db/db/session.py
"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config.settings import DatabaseSettings

settings = DatabaseSettings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
