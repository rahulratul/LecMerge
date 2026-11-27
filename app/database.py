"""SQLite engine, session factory, and declarative Base.

The database URL can be overridden with the ``LECMERGE_DATABASE_URL`` environment
variable (used by tests to point at a temporary SQLite file).
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./lecmerge.db"


class Base(DeclarativeBase):
    """Declarative base class shared by all ORM models."""


def make_engine(database_url: str) -> Engine:
    """Create an engine; for SQLite, allow use across threads and enforce foreign keys."""
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)

    if database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, _record) -> None:  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine: Engine = make_engine(os.environ.get("LECMERGE_DATABASE_URL", DEFAULT_DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(bind: Engine | None = None) -> None:
    """Create all tables if they do not exist (no migration tool for the MVP)."""
    # Import models so their tables are registered on Base.metadata.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=bind or engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a session that is always closed."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
