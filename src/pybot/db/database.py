from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.dialects.sqlite.aiosqlite import AsyncAdapt_aiosqlite_connection
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import ConnectionPoolEntry

from ..core.config import settings


def _is_sqlite_url(database_url: str) -> bool:
    url: URL = make_url(database_url)
    return url.get_backend_name() == "sqlite"


def _attach_sqlite_foreign_keys_pragma(engine: AsyncEngine) -> None:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(
        dbapi_connection: AsyncAdapt_aiosqlite_connection,
        _connection_record: ConnectionPoolEntry,
    ) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_database_engine(database_url: str) -> AsyncEngine:
    if not database_url:
        raise ValueError("Database URL is not configured.")

    engine = create_async_engine(database_url, echo=False)
    if _is_sqlite_url(database_url):
        _attach_sqlite_foreign_keys_pragma(engine)
    return engine


def get_configured_database_engine() -> AsyncEngine:
    """Build database engine using the current runtime settings."""
    return create_database_engine(settings.database_url)
