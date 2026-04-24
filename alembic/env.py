import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from src.pybot.core.config import get_settings
from src.pybot.db.base_class import Base

# Импортируем модели, чтобы Base.metadata собрался
from src.pybot.db.models import *  # noqa: F403  # только для Alembic!

# ====================== НАСТРОЙКИ ПРОЕКТА ======================
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# ====================== ALEMBIC ======================
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _configure_database_url() -> str:
    """Resolve DATABASE_URL from runtime settings and write it into Alembic config."""
    database_url = get_settings().database_url
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)
    return database_url


def do_run_migrations(connection: Connection) -> None:
    """Синхронная функция — ТОЛЬКО ОНА нужна run_sync."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Асинхронный запуск миграций (online mode)."""
    url = _configure_database_url() or config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("DATABASE_URL не настроен в alembic.ini / settings")

    connect_args = {"check_same_thread": False} if "sqlite" in url else {}

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_offline() -> None:
    """Offline mode (редко используется)."""
    url = _configure_database_url() or config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("DATABASE_URL не настроен")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
