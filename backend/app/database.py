"""Database engine, session, and base class for SQLAlchemy models."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db():
    """Yield a database session and ensure it closes after use.

    This is a FastAPI dependency — used with `Depends(get_db)` in endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
