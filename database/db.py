"""Database connection helpers."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base


def get_database_url() -> str | None:
    """Return the configured database URL, if present."""
    load_dotenv()
    return os.getenv("DATABASE_URL")


def get_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine from the configured database URL."""
    url = database_url or get_database_url()
    if not url:
        raise ValueError("DATABASE_URL is not set.")

    return create_engine(url, pool_pre_ping=True)


def create_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Create a configured session factory."""
    db_engine = engine or get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def init_database(engine: Engine | None = None) -> None:
    """Create database tables when they do not already exist."""
    db_engine = engine or get_engine()
    Base.metadata.create_all(bind=db_engine)


@contextmanager
def session_scope(engine: Engine | None = None) -> Iterator[Session]:
    """Provide a transactional session scope."""
    session_factory = create_session_factory(engine)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
