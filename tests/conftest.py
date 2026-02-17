from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.model import Base


@pytest.fixture
def mock_session():
    """Provides a MagicMock pretending to be a SQLAlchemy Session."""
    session = MagicMock()
    return session


@pytest.fixture
def mock_get_session(mock_session):
    """Returns a context-manager factory that yields mock_session."""

    @contextmanager
    def _get_session():
        yield mock_session

    return _get_session


@pytest.fixture
def in_memory_session():
    """Provides a real SQLite in-memory session with tables created."""
    engine = create_engine('sqlite://', echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
