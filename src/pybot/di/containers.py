from collections.abc import AsyncGenerator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ..db.database import engine as global_engine
from ..infrastructure.level_repository import LevelRepository
from ..infrastructure.user_repository import UserRepository
from ..infrastructure.valuation_repository import ValuationRepository
from ..services.users import UserService


class DatabaseProvider(Provider):
    """Провайдеры для БД."""

    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncEngine:
        """Создать Engine ОДИН раз."""
        return global_engine


class SessionProvider(Provider):
    """Провайдер для сессий — НОВАЯ сессия на каждый запрос!"""

    @provide(scope=Scope.REQUEST)
    async def session(self, engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
        """
        Создать НОВУЮ сессию для КАЖДОГО update'а.

        1️⃣  Dishka видит: "нужна AsyncEngine"
        2️⃣  Dishka берет его из APP scope
        3️⃣  Создает новую сессию
        4️⃣  Передает в хэндлер/callback
        5️⃣  После хэндлера → автоматически закрывается
        """
        async_session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session_maker() as session:
            yield session


class RepositoryProvider(Provider):
    """Репозитории — stateless, живут всю программу."""

    @provide(scope=Scope.APP)
    def user_repository(self) -> UserRepository:
        """
        ⚠️  ВАЖНО: репозиторий создается БЕЗ сессии!

        Сессия будет внедрена позже в методы.
        Репозиторий — это просто "конструктор запросов".
        """
        return UserRepository()

    @provide(scope=Scope.APP)
    def level_repository(self) -> LevelRepository:
        """
        ⚠️  ВАЖНО: репозиторий создается БЕЗ сессии!

        Сессия будет внедрена позже в методы.
        Репозиторий — это просто "конструктор запросов".
        """
        return LevelRepository()

    @provide(scope=Scope.APP)
    def valuation_reposiory(self) -> ValuationRepository:
        """
        ⚠️  ВАЖНО: репозиторий создается БЕЗ сессии!

        Сессия будет внедрена позже в методы.
        Репозиторий — это просто "конструктор запросов".
        """
        return ValuationRepository()


class ServiceProvider(Provider):
    """Сервисы — бизнес-логика."""

    @provide(scope=Scope.REQUEST)
    def user_service(
        self,
        db: AsyncSession,  # ← Новая сессия на каждый запрос
        user_repository: UserRepository,  # ← Берется из APP scope
        level_repository: LevelRepository,  # ← Берется из APP scope
    ) -> UserService:
        """Сервис получает репозиторий один раз."""
        return UserService(db, user_repository, level_repository)


async def setup_container() -> AsyncContainer:
    """Собрать контейнер."""
    return make_async_container(
        DatabaseProvider(), SessionProvider(), RepositoryProvider(), ServiceProvider(), AiogramProvider()
    )
