from collections.abc import Sequence
from datetime import date
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import fill_point_db
from src.pybot.core.constants import LevelTypeEnum
from src.pybot.dto import CompetenceReadDTO, UserCreateDTO, UserReadDTO
from src.pybot.dto.value_objects import Points


class FakeRequestContainer:
    def __init__(
        self,
        session: "FakeFillDatabaseSession",
        competence_service: "FakeCompetenceService",
        level_service: "FakeLevelService",
        points_service: "FakePointsService",
        user_service: "FakeFillDatabaseUserService",
    ) -> None:
        self._session = session
        self._competence_service = competence_service
        self._level_service = level_service
        self._points_service = points_service
        self._user_service = user_service

    async def get(
        self,
        dep_type: type[AsyncSession]
        | type[fill_point_db.CompetenceService]
        | type[fill_point_db.LevelService]
        | type[fill_point_db.PointsService]
        | type[fill_point_db.UserService],
    ) -> "FakeFillDatabaseSession | FakeCompetenceService | FakeLevelService | FakePointsService | FakeFillDatabaseUserService":
        if dep_type is AsyncSession:
            return self._session
        if dep_type is fill_point_db.CompetenceService:
            return self._competence_service
        if dep_type is fill_point_db.LevelService:
            return self._level_service
        if dep_type is fill_point_db.PointsService:
            return self._points_service
        if dep_type is fill_point_db.UserService:
            return self._user_service
        raise AssertionError(f"Unexpected dependency request: {dep_type!r}")


class _RequestScope:
    def __init__(self, request_container: FakeRequestContainer) -> None:
        self._request_container = request_container

    async def __aenter__(self) -> FakeRequestContainer:
        return self._request_container

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class _ContainerStub:
    def __init__(self, request_container: FakeRequestContainer) -> None:
        self._request_container = request_container
        self.close = AsyncMock()

    def __call__(self) -> _RequestScope:
        return _RequestScope(self._request_container)


class FakeFillDatabaseSession:
    def __init__(self) -> None:
        self.rollback_mock = AsyncMock()

    async def rollback(self) -> None:
        await self.rollback_mock()


class FakeCompetenceService:
    pass


class FakeLevelService(fill_point_db.LevelService):
    def __init__(self) -> None:
        pass


class FakePointsService(fill_point_db.PointsService):
    def __init__(self) -> None:
        pass


class FakeFillDatabaseUserService(fill_point_db.UserService):
    def __init__(self) -> None:
        pass


class FakeGenerateUsersService(fill_point_db.UserService):
    def __init__(self, created_user: UserReadDTO) -> None:
        self.register_student_mock = AsyncMock(return_value=created_user)
        self.add_user_competencies_mock = AsyncMock(return_value=created_user)

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        return await self.register_student_mock(dto)

    async def add_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        return await self.add_user_competencies_mock(user_id, competence_ids)


class FakeGenerateUsersPointsService(fill_point_db.PointsService):
    def __init__(self, updated_user: UserReadDTO) -> None:
        self.update_user_points_by_id_mock = AsyncMock(return_value=updated_user)

    async def update_user_points_by_id(
        self,
        user_id: int,
        points_value: int,
        points_type: LevelTypeEnum,
    ) -> UserReadDTO:
        return await self.update_user_points_by_id_mock(user_id, points_value, points_type)


@pytest.mark.asyncio
async def test_fill_database_uses_dishka_container_and_closes_it(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_session = FakeFillDatabaseSession()
    fake_competence_service = FakeCompetenceService()
    fake_level_service = FakeLevelService()
    fake_points_service = FakePointsService()
    fake_user_service = FakeFillDatabaseUserService()
    fake_request_container = FakeRequestContainer(
        fake_session,
        fake_competence_service,
        fake_level_service,
        fake_points_service,
        fake_user_service,
    )
    fake_container = _ContainerStub(fake_request_container)

    setup_container = AsyncMock(return_value=fake_container)
    generate_levels_data = AsyncMock()
    add_roles_data = AsyncMock()
    competencies = [CompetenceReadDTO(id=1, name="Python", description=None)]
    add_competencies_data = AsyncMock(return_value=competencies)
    generate_users_data = AsyncMock()

    monkeypatch.setattr(fill_point_db, "setup_container", setup_container)
    monkeypatch.setattr(fill_point_db, "generate_levels_data", generate_levels_data)
    monkeypatch.setattr(fill_point_db, "add_roles_data", add_roles_data)
    monkeypatch.setattr(fill_point_db, "add_competencies_data", add_competencies_data)
    monkeypatch.setattr(fill_point_db, "generate_users_data", generate_users_data)

    await fill_point_db.fill_database()

    setup_container.assert_awaited_once_with()
    generate_levels_data.assert_awaited_once_with(fake_session, fake_level_service)
    add_roles_data.assert_awaited_once_with(fake_session)
    add_competencies_data.assert_awaited_once_with(fake_competence_service)
    generate_users_data.assert_awaited_once_with(
        fake_user_service,
        fake_points_service,
        competencies,
        fill_point_db.NUM_FAKE_USERS,
    )
    fake_session.rollback_mock.assert_not_awaited()
    fake_container.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_users_data_uses_services_for_registration_and_points(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_user = UserReadDTO(
        id=42,
        first_name="Иван",
        last_name="Иванов",
        patronymic="Иванович",
        telegram_id=fill_point_db.MIN_TELEGRAM_ID,
        academic_points=Points(value=0, point_type=LevelTypeEnum.ACADEMIC),
        reputation_points=Points(value=0, point_type=LevelTypeEnum.REPUTATION),
        join_date=date(2026, 3, 13),
    )
    fake_user_service = FakeGenerateUsersService(fake_user)
    fake_points_service = FakeGenerateUsersPointsService(fake_user)

    monkeypatch.setattr(
        fill_point_db,
        "fake",
        type(
            "FakeFaker",
            (),
            {
                "first_name": staticmethod(lambda: "Иван"),
                "last_name": staticmethod(lambda: "Иванов"),
                "middle_name": staticmethod(lambda: "Иванович"),
                "phone_number": staticmethod(lambda: "+7 (999) 123-45-67"),
                "boolean": staticmethod(lambda chance_of_getting_true=80: True),
            },
        )(),
    )
    monkeypatch.setattr(fill_point_db.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(fill_point_db.random, "randrange", lambda start, stop, step: step)
    monkeypatch.setattr(fill_point_db.random, "randint", lambda start, end: 1)
    monkeypatch.setattr(fill_point_db.random, "sample", lambda population, k: [population[0]])

    competencies = [CompetenceReadDTO(id=7, name="Python", description=None)]

    await fill_point_db.generate_users_data(fake_user_service, fake_points_service, competencies, 1)

    fake_user_service.register_student_mock.assert_awaited_once()
    assert fake_user_service.register_student_mock.await_args is not None
    created_dto = fake_user_service.register_student_mock.await_args.args[0]
    assert created_dto.first_name == "Иван"
    assert created_dto.last_name == "Иванов"
    assert created_dto.patronymic == "Иванович"
    assert created_dto.phone == "+79991234567"
    assert created_dto.tg_id == fill_point_db.MIN_TELEGRAM_ID

    assert fake_points_service.update_user_points_by_id_mock.await_count == 2
    fake_user_service.add_user_competencies_mock.assert_awaited_once_with(42, [7])
