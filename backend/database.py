"""Database setup for the DukaanAI backend."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dukaanai.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables() -> None:
    """Create missing application tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a database session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
