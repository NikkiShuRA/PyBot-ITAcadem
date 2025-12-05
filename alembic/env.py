import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from alembic import context
from src.pybot.core.config import settings
from src.pybot.db.base_class import Base
from src.pybot.db.models import *  # noqa: F403

# --- НАЧАЛО ВАЖНОЙ ЧАСТИ ---

# Добавляем твою папку src в пути Python, чтобы Alembic мог найти твои модули
# Это нужно, чтобы Alembic "увидел" твои модели из src/pybot/db/models
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Импортируем твою базовую модель и настройки


# Импортируем все модели, чтобы Base.metadata наполнился
# Alembic будет использовать этот metadata для автогенерации миграций


# --- КОНЕЦ ВАЖНОЙ ЧАСТИ ---

# Это конфигурация Alembic, которая считывается из alembic.ini
config = context.config

# Интерпретируем файл конфигурации для логирования Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем DATABASE_URL в конфигурации из твоих Pydantic-настроек
# Это связывает alembic.ini с твоим config.py
config.set_main_option("sqlalchemy.url", settings.database_url)

# Устанавливаем target_metadata для автогенерации Alembic
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: AsyncSession) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
