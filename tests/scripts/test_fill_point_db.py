import asyncio
import inspect
import os
from pathlib import Path
import subprocess
import sys
from collections.abc import Coroutine, Sequence
from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import fill_point_db
from src.pybot.core.constants import LevelTypeEnum
from src.pybot.dto import AdjustUserPointsDTO, CompetenceCreateDTO, CompetenceReadDTO, UserCreateDTO, UserReadDTO
from src.pybot.dto.value_objects import Points


class FakeRequestContainer:
    def __init__(
        self,
        session: "FakeFillDatabaseSession",
        competence_service: "FakeCompetenceService",
        level_service: "FakeLevelService",
        points_service: "FakePointsService",
        user_competence_service: "FakeUserCompetenceService",
        user_service: "FakeFillDatabaseUserService",
    ) -> None:
        self._session = session
        self._competence_service = competence_service
        self._level_service = level_service
        self._points_service = points_service
        self._user_competence_service = user_competence_service
        self._user_service = user_service

    async def get(
        self,
        dep_type: type[AsyncSession]
        | type[fill_point_db.CompetenceService]
        | type[fill_point_db.LevelService]
        | type[fill_point_db.PointsService]
        | type[fill_point_db.UserCompetenceService]
        | type[fill_point_db.UserService],
    ) -> "FakeFillDatabaseSession | FakeCompetenceService | FakeLevelService | FakePointsService | FakeUserCompetenceService | FakeFillDatabaseUserService":
        if dep_type is AsyncSession:
            return self._session
        if dep_type is fill_point_db.CompetenceService:
            return self._competence_service
        if dep_type is fill_point_db.LevelService:
            return self._level_service
        if dep_type is fill_point_db.PointsService:
            return self._points_service
        if dep_type is fill_point_db.UserCompetenceService:
            return self._user_competence_service
        if dep_type is fill_point_db.UserService:
            return self._user_service
        raise AssertionError(f"Unexpected dependency request: {dep_type!r}")


class _RequestScope:
    def __init__(self, request_container: FakeRequestContainer) -> None:
        self._request_container = request_container

    async def __aenter__(self) -> FakeRequestContainer:
        return self._request_container

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        del exc_type, exc, tb
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


class FakeUserCompetenceService(fill_point_db.UserCompetenceService):
    def __init__(self) -> None:
        pass


class FakeFillDatabaseUserService(fill_point_db.UserService):
    def __init__(self) -> None:
        pass


class FakeGenerateUsersService(fill_point_db.UserService):
    def __init__(self, created_user: UserReadDTO) -> None:
        self.register_student_mock = AsyncMock(return_value=created_user)

    async def register_student(self, dto: UserCreateDTO) -> UserReadDTO:
        return await self.register_student_mock(dto)


class FakeGenerateUsersCompetenceService(fill_point_db.UserCompetenceService):
    def __init__(self, updated_user: UserReadDTO) -> None:
        self.add_user_competencies_mock = AsyncMock(return_value=updated_user)

    async def add_user_competencies(self, user_id: int, competence_ids: Sequence[int]) -> UserReadDTO:
        return await self.add_user_competencies_mock(user_id, competence_ids)


class FakeGenerateUsersPointsService(fill_point_db.PointsService):
    def __init__(self, updated_user: UserReadDTO) -> None:
        self.change_points_mock = AsyncMock(return_value=updated_user)

    async def change_points(self, dto: AdjustUserPointsDTO) -> UserReadDTO:
        return await self.change_points_mock(dto)


class FakeFaker:
    @staticmethod
    def first_name() -> str:
        return "\u0418\u0432\u0430\u043d"

    @staticmethod
    def last_name() -> str:
        return "\u0418\u0432\u0430\u043d\u043e\u0432"

    @staticmethod
    def middle_name() -> str:
        return "\u0418\u0432\u0430\u043d\u043e\u0432\u0438\u0447"

    @staticmethod
    def phone_number() -> str:
        return "+7 (999) 123-45-67"

    @staticmethod
    def boolean(chance_of_getting_true: int = 80) -> bool:
        del chance_of_getting_true
        return True


def build_runtime_dependencies(
    *,
    setup_container: AsyncMock | None = None,
) -> fill_point_db.RuntimeDependencies:
    return fill_point_db.RuntimeDependencies(
        level_type_enum=LevelTypeEnum,
        role_enum=fill_point_db.RoleEnum,
        level_model=fill_point_db.Level,
        role_model=fill_point_db.Role,
        setup_container=setup_container or AsyncMock(),
        adjust_user_points_dto_cls=AdjustUserPointsDTO,
        competence_create_dto_cls=CompetenceCreateDTO,
        competence_read_dto_cls=CompetenceReadDTO,
        user_create_dto_cls=UserCreateDTO,
        points_cls=Points,
        competence_service_cls=fill_point_db.CompetenceService,
        level_service_cls=fill_point_db.LevelService,
        points_service_cls=fill_point_db.PointsService,
        user_competence_service_cls=fill_point_db.UserCompetenceService,
        user_service_cls=fill_point_db.UserService,
    )


def test_build_seed_config_preserves_default_runtime_behavior() -> None:
    cli_config = fill_point_db.FillDatabaseCLIConfig()

    runtime_config = fill_point_db.build_seed_config(cli_config)

    assert runtime_config == fill_point_db.FillDatabaseConfig()


def test_build_seed_config_inverts_skip_flags() -> None:
    cli_config = fill_point_db.FillDatabaseCLIConfig(
        skip_levels=True,
        skip_roles=True,
        skip_competencies=True,
        skip_fake_users=True,
        competencies_preset="none",
    )

    runtime_config = fill_point_db.build_seed_config(cli_config)

    assert runtime_config.seed_levels is False
    assert runtime_config.seed_roles is False
    assert runtime_config.seed_competencies is False
    assert runtime_config.seed_fake_users is False
    assert runtime_config.competencies_preset is fill_point_db.CompetencePreset.NONE


def test_parse_cli_args_parses_tyro_dataclass_config() -> None:
    cli_config = fill_point_db.parse_cli_args(
        [
            "--num-fake-users",
            "3",
            "--num-levels-per-type",
            "2",
            "--min-telegram-id",
            "2000000000",
            "--competencies-preset",
            "none",
            "--skip-levels",
            "--skip-fake-users",
        ]
    )

    assert cli_config.num_fake_users == 3
    assert cli_config.num_levels_per_type == 2
    assert cli_config.min_telegram_id == 2_000_000_000
    assert cli_config.competencies_preset == "none"
    assert cli_config.skip_levels is True
    assert cli_config.skip_fake_users is True
    assert cli_config.skip_roles is False


def test_main_uses_tyro_cli_and_asyncio_run(monkeypatch: pytest.MonkeyPatch) -> None:
    cli_config = fill_point_db.FillDatabaseCLIConfig(
        num_fake_users=3,
        skip_levels=True,
        competencies_preset="none",
    )
    expected_runtime_config = fill_point_db.build_seed_config(cli_config)
    tyro_cli_mock = Mock(return_value=cli_config)
    ensure_project_root_mock = Mock()
    observed: dict[str, object] = {}
    original_asyncio_run = asyncio.run

    async def fake_fill_database(config: fill_point_db.FillDatabaseConfig | None = None) -> str:
        observed["runtime_config"] = config
        return "ok"

    def fake_asyncio_run(coro: Coroutine[object, object, str]) -> str:
        observed["is_coroutine"] = inspect.iscoroutine(coro)
        return original_asyncio_run(coro)

    monkeypatch.setattr(fill_point_db.tyro, "cli", tyro_cli_mock)
    monkeypatch.setattr(fill_point_db, "_ensure_project_root_on_path", ensure_project_root_mock)
    monkeypatch.setattr(fill_point_db, "fill_database", fake_fill_database)
    monkeypatch.setattr(fill_point_db.asyncio, "run", fake_asyncio_run)

    fill_point_db.main()

    tyro_cli_mock.assert_called_once_with(fill_point_db.FillDatabaseCLIConfig, args=None)
    ensure_project_root_mock.assert_called_once_with()
    assert observed["is_coroutine"] is True
    assert observed["runtime_config"] == expected_runtime_config


def test_fill_point_db_help_does_not_require_runtime_env(tmp_path: Path) -> None:
    script_file = fill_point_db.__file__
    if script_file is None:
        raise AssertionError("fill_point_db module does not define __file__")
    script_path = Path(script_file).resolve()
    runtime_env = os.environ.copy()
    for key in ("BOT_TOKEN", "BOT_TOKEN_TEST", "ROLE_REQUEST_ADMIN_TG_ID", "DATABASE_URL"):
        runtime_env.pop(key, None)

    result = subprocess.run(  # noqa: S603
        [sys.executable, str(script_path), "--help"],  # noqa: S607
        capture_output=True,
        check=False,
        cwd=tmp_path,
        env=runtime_env,
        text=True,
    )

    assert result.returncode == 0
    assert "Public CLI configuration for database seed generation." in result.stdout
    assert "BOT_TOKEN" not in result.stderr


@pytest.mark.asyncio
async def test_fill_database_uses_dishka_container_and_closes_it(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_session = FakeFillDatabaseSession()
    fake_competence_service = FakeCompetenceService()
    fake_level_service = FakeLevelService()
    fake_points_service = FakePointsService()
    fake_user_competence_service = FakeUserCompetenceService()
    fake_user_service = FakeFillDatabaseUserService()
    fake_request_container = FakeRequestContainer(
        fake_session,
        fake_competence_service,
        fake_level_service,
        fake_points_service,
        fake_user_competence_service,
        fake_user_service,
    )
    fake_container = _ContainerStub(fake_request_container)

    config = fill_point_db.FillDatabaseConfig(num_fake_users=7)
    setup_container = AsyncMock(return_value=fake_container)
    generate_levels_data = AsyncMock()
    add_roles_data = AsyncMock()
    competencies = [CompetenceReadDTO(id=1, name="Python", description=None)]
    add_competencies_data = AsyncMock(return_value=competencies)
    generate_users_data = AsyncMock()

    monkeypatch.setattr(
        fill_point_db,
        "_get_runtime_dependencies",
        Mock(return_value=build_runtime_dependencies(setup_container=setup_container)),
    )
    monkeypatch.setattr(fill_point_db, "_get_runtime_logger", Mock(return_value=Mock()))
    monkeypatch.setattr(fill_point_db, "generate_levels_data", generate_levels_data)
    monkeypatch.setattr(fill_point_db, "add_roles_data", add_roles_data)
    monkeypatch.setattr(fill_point_db, "add_competencies_data", add_competencies_data)
    monkeypatch.setattr(fill_point_db, "generate_users_data", generate_users_data)

    await fill_point_db.fill_database(config)

    setup_container.assert_awaited_once_with()
    generate_levels_data.assert_awaited_once_with(fake_session, fake_level_service, config)
    add_roles_data.assert_awaited_once_with(fake_session)
    add_competencies_data.assert_awaited_once_with(fake_competence_service, config)
    generate_users_data.assert_awaited_once_with(
        fake_user_service,
        fake_user_competence_service,
        fake_points_service,
        competencies,
        config,
    )
    fake_session.rollback_mock.assert_not_awaited()
    fake_container.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_fill_database_skips_disabled_seed_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_session = FakeFillDatabaseSession()
    fake_request_container = FakeRequestContainer(
        fake_session,
        FakeCompetenceService(),
        FakeLevelService(),
        FakePointsService(),
        FakeUserCompetenceService(),
        FakeFillDatabaseUserService(),
    )
    fake_container = _ContainerStub(fake_request_container)

    generate_levels_data = AsyncMock()
    add_roles_data = AsyncMock()
    add_competencies_data = AsyncMock()
    generate_users_data = AsyncMock()

    monkeypatch.setattr(
        fill_point_db,
        "_get_runtime_dependencies",
        Mock(return_value=build_runtime_dependencies(setup_container=AsyncMock(return_value=fake_container))),
    )
    monkeypatch.setattr(fill_point_db, "_get_runtime_logger", Mock(return_value=Mock()))
    monkeypatch.setattr(fill_point_db, "generate_levels_data", generate_levels_data)
    monkeypatch.setattr(fill_point_db, "add_roles_data", add_roles_data)
    monkeypatch.setattr(fill_point_db, "add_competencies_data", add_competencies_data)
    monkeypatch.setattr(fill_point_db, "generate_users_data", generate_users_data)

    await fill_point_db.fill_database(
        fill_point_db.FillDatabaseConfig(
            seed_levels=False,
            seed_roles=False,
            seed_competencies=False,
            seed_fake_users=False,
        )
    )

    generate_levels_data.assert_not_awaited()
    add_roles_data.assert_not_awaited()
    add_competencies_data.assert_not_awaited()
    generate_users_data.assert_not_awaited()
    fake_session.rollback_mock.assert_not_awaited()
    fake_container.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_users_data_uses_services_for_registration_and_points(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = fill_point_db.FillDatabaseConfig(
        num_fake_users=1,
        min_telegram_id=1_555_000_000,
        seed_points_reason="Configured seed reason",
    )
    fake_user = UserReadDTO(
        id=42,
        first_name="\u0418\u0432\u0430\u043d",
        last_name="\u0418\u0432\u0430\u043d\u043e\u0432",
        patronymic="\u0418\u0432\u0430\u043d\u043e\u0432\u0438\u0447",
        telegram_id=config.min_telegram_id,
        academic_points=Points(value=0, point_type=LevelTypeEnum.ACADEMIC),
        reputation_points=Points(value=0, point_type=LevelTypeEnum.REPUTATION),
        join_date=date(2026, 3, 13),
    )
    fake_user_service = FakeGenerateUsersService(fake_user)
    fake_user_competence_service = FakeGenerateUsersCompetenceService(fake_user)
    fake_points_service = FakeGenerateUsersPointsService(fake_user)

    monkeypatch.setattr(fill_point_db, "_get_runtime_dependencies", Mock(return_value=build_runtime_dependencies()))
    monkeypatch.setattr(fill_point_db, "_build_faker", lambda _: FakeFaker())
    monkeypatch.setattr(fill_point_db.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(fill_point_db.random, "randrange", lambda start, stop, step: step)
    monkeypatch.setattr(fill_point_db.random, "randint", lambda start, end: 1)
    monkeypatch.setattr(fill_point_db.random, "sample", lambda population, k: [population[0]])

    competencies = [CompetenceReadDTO(id=7, name="Python", description=None)]

    await fill_point_db.generate_users_data(
        fake_user_service,
        fake_user_competence_service,
        fake_points_service,
        competencies,
        config,
    )

    fake_user_service.register_student_mock.assert_awaited_once()
    register_call = fake_user_service.register_student_mock.await_args
    if register_call is None:
        raise AssertionError("register_student was not awaited")
    created_dto = register_call.args[0]
    assert created_dto.first_name == "\u0418\u0432\u0430\u043d"
    assert created_dto.last_name == "\u0418\u0432\u0430\u043d\u043e\u0432"
    assert created_dto.patronymic == "\u0418\u0432\u0430\u043d\u043e\u0432\u0438\u0447"
    assert created_dto.phone == "+79991234567"
    assert created_dto.tg_id == config.min_telegram_id

    assert fake_points_service.change_points_mock.await_count == 2
    academic_dto = fake_points_service.change_points_mock.await_args_list[0].args[0]
    reputation_dto = fake_points_service.change_points_mock.await_args_list[1].args[0]
    assert academic_dto.recipient_id == 42
    assert academic_dto.giver_id == 42
    assert academic_dto.points == Points(value=5, point_type=LevelTypeEnum.ACADEMIC)
    assert academic_dto.reason == config.seed_points_reason
    assert reputation_dto.points == Points(value=5, point_type=LevelTypeEnum.REPUTATION)
    fake_user_competence_service.add_user_competencies_mock.assert_awaited_once_with(42, [7])


@pytest.mark.asyncio
async def test_generate_users_data_skips_zero_points_adjustments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = fill_point_db.FillDatabaseConfig(num_fake_users=1)
    fake_user = UserReadDTO(
        id=42,
        first_name="\u0418\u0432\u0430\u043d",
        last_name="\u0418\u0432\u0430\u043d\u043e\u0432",
        patronymic="\u0418\u0432\u0430\u043d\u043e\u0432\u0438\u0447",
        telegram_id=config.min_telegram_id,
        academic_points=Points(value=0, point_type=LevelTypeEnum.ACADEMIC),
        reputation_points=Points(value=0, point_type=LevelTypeEnum.REPUTATION),
        join_date=date(2026, 3, 13),
    )
    fake_user_service = FakeGenerateUsersService(fake_user)
    fake_user_competence_service = FakeGenerateUsersCompetenceService(fake_user)
    fake_points_service = FakeGenerateUsersPointsService(fake_user)

    monkeypatch.setattr(fill_point_db, "_get_runtime_dependencies", Mock(return_value=build_runtime_dependencies()))
    monkeypatch.setattr(fill_point_db, "_build_faker", lambda _: FakeFaker())
    monkeypatch.setattr(fill_point_db.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(fill_point_db.random, "randrange", lambda start, stop, step: 0)

    await fill_point_db.generate_users_data(
        fake_user_service,
        fake_user_competence_service,
        fake_points_service,
        [],
        config,
    )

    fake_points_service.change_points_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_competencies_data_uses_selected_preset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_competence = CompetenceReadDTO(id=1, name="Python", description="desc")
    competence_service = AsyncMock()
    competence_service.find_all_competencies = AsyncMock(return_value=[])
    competence_service.create_competence = AsyncMock(return_value=created_competence)
    monkeypatch.setattr(fill_point_db, "_get_runtime_dependencies", Mock(return_value=build_runtime_dependencies()))
    monkeypatch.setitem(
        fill_point_db._COMPETENCE_PRESETS,
        fill_point_db.CompetencePreset.PROFESSIONALS,
        (fill_point_db.CompetenceSeedConfig(name="Python", description="desc"),),
    )
    config = fill_point_db.FillDatabaseConfig(
        competencies_preset=fill_point_db.CompetencePreset.PROFESSIONALS,
    )

    result = await fill_point_db.add_competencies_data(competence_service, config)

    competence_service.create_competence.assert_awaited_once()
    create_call = competence_service.create_competence.await_args
    if create_call is None:
        raise AssertionError("create_competence was not awaited")
    dto = create_call.args[0]
    assert dto.name == "Python"
    assert dto.description == "desc"
    assert result == [created_competence]


@pytest.mark.asyncio
async def test_add_competencies_data_skips_empty_preset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    competence_service = AsyncMock()
    competence_service.find_all_competencies = AsyncMock(return_value=[])
    competence_service.create_competence = AsyncMock()
    config = fill_point_db.FillDatabaseConfig(
        competencies_preset=fill_point_db.CompetencePreset.NONE,
    )

    monkeypatch.setattr(fill_point_db, "_get_runtime_dependencies", Mock(return_value=build_runtime_dependencies()))
    result = await fill_point_db.add_competencies_data(competence_service, config)

    competence_service.create_competence.assert_not_awaited()
    assert result == []
