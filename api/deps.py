"""FastAPI dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from database.db import create_session_factory


def get_db() -> Generator[Session, None, None]:
    """Yield one database session for a request."""
    session_factory = create_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
