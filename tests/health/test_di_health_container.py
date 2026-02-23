import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from pybot.di import containers as di_containers
from pybot.services.health import HealthService


@pytest.mark.asyncio
async def test_setup_health_container_smoke_resolves_key_dependencies() -> None:
    """Smoke test for health DI container assembly."""
    container = di_containers.setup_health_container()
    try:
        engine = await container.get(AsyncEngine)
        async with container() as request_container:
            session = await request_container.get(AsyncSession)
            health_service = await request_container.get(HealthService)

        assert engine is not None
        assert session is not None
        assert isinstance(health_service, HealthService)
    finally:
        await container.close()


@pytest.mark.asyncio
async def test_health_container_lifecycle_closes_session_and_disposes_engine(
    monkeypatch: pytest.MonkeyPatch,
    mocker,
) -> None:
    """Verify health container closes request session and disposes DB engine."""

    class FakeEngine:
        def __init__(self) -> None:
            self.dispose = mocker.AsyncMock()

    class FakeSession:
        def __init__(self) -> None:
            self.close = mocker.AsyncMock()

    class FakeSessionContext:
        def __init__(self, session: FakeSession) -> None:
            self._session = session

        async def __aenter__(self) -> FakeSession:
            return self._session

        async def __aexit__(self, exc_type, exc, tb) -> None:
            await self._session.close()

    class FakeSessionMaker:
        def __init__(self, session: FakeSession) -> None:
            self._session = session

        def __call__(self) -> FakeSessionContext:
            return FakeSessionContext(self._session)

    fake_engine = FakeEngine()
    fake_session = FakeSession()

    def fake_async_sessionmaker(*args, **kwargs) -> FakeSessionMaker:
        return FakeSessionMaker(fake_session)

    monkeypatch.setattr(di_containers, "global_engine", fake_engine)
    monkeypatch.setattr(di_containers, "async_sessionmaker", fake_async_sessionmaker)

    container = di_containers.setup_health_container()
    async with container() as request_container:
        session = await request_container.get(AsyncSession)
        assert session is fake_session

    fake_session.close.assert_awaited_once()

    await container.close()
    fake_engine.dispose.assert_awaited_once()
