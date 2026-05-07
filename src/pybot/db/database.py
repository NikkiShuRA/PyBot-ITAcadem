from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.dialects.sqlite.aiosqlite import AsyncAdapt_aiosqlite_connection
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import ConnectionPoolEntry


def _is_sqlite_url(database_url: str) -> bool:
    """Проверяет, является ли URL базы данных адресом SQLite.

    Args:
        database_url: Строка подключения к базе данных.

    Returns:
        bool: True, если бэкенд — sqlite, иначе False.
    """
    url: URL = make_url(database_url)
    return url.get_backend_name() == "sqlite"


def _attach_sqlite_foreign_keys_pragma(engine: AsyncEngine) -> None:
    """Прикрепляет обработчик события для включения внешних ключей в SQLite.

    SQLite по умолчанию не проверяет ограничения внешних ключей. Этот метод
    настраивает движок на выполнение 'PRAGMA foreign_keys=ON' при каждом подключении.

    Args:
        engine: Асинхронный движок SQLAlchemy.
    """

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(
        dbapi_connection: AsyncAdapt_aiosqlite_connection,
        _connection_record: ConnectionPoolEntry,
    ) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_database_engine(database_url: str) -> AsyncEngine:
    """Создает и настраивает асинхронный движок базы данных.

    Если используется SQLite, автоматически включает поддержку внешних ключей.

    Args:
        database_url: Строка подключения к базе данных.

    Returns:
        AsyncEngine: Сконфигурированный асинхронный движок SQLAlchemy.

    Raises:
        ValueError: Если URL базы данных не настроен.
    """
    if not database_url:
        raise ValueError("Database URL is not configured.")

    engine = create_async_engine(database_url, echo=False)
    if _is_sqlite_url(database_url):
        _attach_sqlite_foreign_keys_pragma(engine)
    return engine
