from __future__ import annotations

from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

__test__ = False


class TestDatabaseProvider(Provider):
    """Dishka provider for isolated test database dependencies."""

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__()
        self._engine = engine

    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        return self._engine

    @provide(scope=Scope.APP)
    def provide_session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session
