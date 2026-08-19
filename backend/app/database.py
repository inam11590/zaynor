"""Database engine, session, and base class for SQLAlchemy models."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./zaynor.db")

# Render PostgreSQL: fix dialect prefix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Render PostgreSQL requires SSL
connect_args = {}
if "psycopg2" in DATABASE_URL:
    connect_args = {"sslmode": "require"}
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
elif DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        echo=False,
    )
else:
    engine = create_engine(DATABASE_URL)

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
