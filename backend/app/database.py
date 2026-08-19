"""Database engine, session, and base class for SQLAlchemy models."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

DATABASE_URL = settings.DATABASE_URL

# Render PostgreSQL requires the psycopg2 dialect
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Render PostgreSQL requires SSL
connect_args = {}
if "postgresql" in DATABASE_URL:
    connect_args = {"sslmode": "require"}
elif DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db():
    """Yield a database session and ensure it closes after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
