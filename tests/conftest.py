from __future__ import annotations

import random
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from dishka import AsyncContainer, make_async_container
from faker import Faker
from sqlalchemy import event, func, select
from sqlalchemy.dialects.sqlite.aiosqlite import AsyncAdapt_aiosqlite_connection
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapper
from sqlalchemy.pool import ConnectionPoolEntry

from pybot.core.config import settings
from pybot.db.models import Base
from pybot.db.models.role_module.role_request import RoleRequest
from pybot.di.containers import DomainServiceProvider, HealthProvider, RepositoryProvider, ServiceProvider
from tests.providers import TestDatabaseProvider, TestOverridesProvider


@event.listens_for(RoleRequest, "before_insert")
def assign_sqlite_role_request_id(
    _mapper: Mapper[RoleRequest],
    connection: Connection,
    target: RoleRequest,
) -> None:
    """Provide sequence-like ids for SQLite tests where BigInteger PK is not autoincremented."""
    if target.id is not None:
        return

    max_id_stmt = select(func.max(RoleRequest.id))
    max_id = connection.execute(max_id_stmt).scalar_one_or_none()
    target.id = 1 if max_id is None else int(max_id) + 1


@pytest.fixture(autouse=True)
def faker_seed() -> Generator[None, None, None]:
    """Seed all pseudo-random generators for deterministic tests."""
    random.seed(42)
    Faker.seed(42)
    yield


@pytest.fixture
def test_db_path(tmp_path: Path, request: pytest.FixtureRequest) -> Path:
    """Create isolated SQLite file path per test scenario."""
    safe_name = request.node.name.replace("[", "_").replace("]", "_")
    return tmp_path / f"{safe_name}.sqlite3"


@pytest.fixture
def test_database_url(test_db_path: Path) -> str:
    return f"sqlite+aiosqlite:///{test_db_path.as_posix()}"


@pytest.fixture(autouse=True)
def settings_overrides(monkeypatch: pytest.MonkeyPatch, test_database_url: str) -> Generator[None, None, None]:
    """Override runtime settings for CI-safe test isolation."""
    monkeypatch.setattr(settings, "database_url", test_database_url)
    monkeypatch.setattr(settings, "bot_mode", "test")
    monkeypatch.setattr(settings, "bot_token", "123456:TEST_TOKEN")
    monkeypatch.setattr(settings, "bot_token_test", "123456:TEST_TOKEN")
    monkeypatch.setattr(settings, "role_request_admin_tg_id", 999999999)
    monkeypatch.setattr(settings, "health_api_enabled", False)
    yield


@pytest_asyncio.fixture
async def test_engine(settings_overrides: None, test_database_url: str) -> AsyncGenerator[AsyncEngine, None]:
    """Create isolated async SQLAlchemy engine with FK enforcement."""
    engine = create_async_engine(test_database_url, echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(
        dbapi_connection: AsyncAdapt_aiosqlite_connection,
        _connection_record: ConnectionPoolEntry,
    ) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def create_schema(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Create all DB tables before each test and drop them afterwards."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def db_session_maker(
    create_schema: None,
    test_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(
    db_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Request-scoped async session with explicit teardown."""
    async with db_session_maker() as session:
        try:
            yield session
        finally:
            if session.in_transaction():
                await session.rollback()


@pytest_asyncio.fixture
async def dishka_test_container(
    create_schema: None,
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncContainer, None]:
    """Build isolated Dishka test container with fake outbound adapters."""
    container = make_async_container(
        TestDatabaseProvider(test_engine),
        RepositoryProvider(),
        ServiceProvider(),
        DomainServiceProvider(),
        HealthProvider(),
        TestOverridesProvider(),
    )

    try:
        yield container
    finally:
        await container.close()


@pytest_asyncio.fixture
async def dishka_request_container(
    dishka_test_container: AsyncContainer,
) -> AsyncGenerator[AsyncContainer, None]:
    """Open Dishka request scope for service-level tests."""
    async with dishka_test_container() as request_container:
        yield request_container
