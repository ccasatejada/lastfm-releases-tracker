# db/database.py
import os
from collections.abc import Generator
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

# Construction de l'URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    user = os.getenv('DATABASE_USER')
    password = os.getenv('DATABASE_PASSWORD')
    host = os.getenv('DATABASE_HOST', 'localhost')
    db_name = os.getenv('DATABASE_SCHEMA')
    database_url = f'postgresql+psycopg://{user}:{password}@{host}/{db_name}'

# Engine global
engine = create_engine(
    database_url, echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10
)

# SessionLocal factory
SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


@contextmanager
def get_session() -> Generator:
    """
    Context manager pour gérer automatiquement les sessions.

    Usage:
        with get_session() as session:
            user = session.get(AppUser, 1)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Session:
    return SessionLocal()
