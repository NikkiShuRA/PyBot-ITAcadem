"""Seed script for filling the database with test data.

The script uses tyro as its public CLI while preserving the current async
Dishka-based bootstrap flow behind a dedicated runtime configuration object.
"""

from __future__ import annotations

import asyncio
import enum
import os
import random
import sys
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module
from typing import TYPE_CHECKING, Literal, TypedDict

import tyro
from faker import Faker
from loguru import logger as loguru_logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from dishka import AsyncContainer
    from loguru import Logger

    from src.pybot.core.constants import PointsTypeEnum, RoleEnum
    from src.pybot.db.models import Level, Role
    from src.pybot.dto import AdjustUserPointsDTO, CompetenceCreateDTO, CompetenceReadDTO, UserCreateDTO
    from src.pybot.dto.value_objects import Points
    from src.pybot.services import CompetenceService, LevelService, PointsService, UserCompetenceService, UserService
else:

    class PointsTypeEnum(enum.StrEnum):
        ACADEMIC = "academic"
        REPUTATION = "reputation"

    class RoleEnum(enum.StrEnum):
        STUDENT = "Student"
        MENTOR = "Mentor"
        ADMIN = "Admin"

    class Level:
        pass

    class Role:
        pass

    class AdjustUserPointsDTO:
        def __init__(
            self,
            recipient_id: int,
            giver_id: int,
            points: Points,
            reason: str,
        ) -> None:
            del recipient_id, giver_id, points, reason
            raise RuntimeError("fill_point_db runtime dependencies are not loaded")

    class CompetenceCreateDTO:
        def __init__(self, name: str, description: str) -> None:
            del name, description
            raise RuntimeError("fill_point_db runtime dependencies are not loaded")

    class CompetenceReadDTO:
        id: int

    class UserCreateDTO:
        def __init__(
            self,
            first_name: str,
            last_name: str,
            patronymic: str | None,
            phone: str,
            tg_id: int,
        ) -> None:
            del first_name, last_name, patronymic, phone, tg_id
            raise RuntimeError("fill_point_db runtime dependencies are not loaded")

    class Points:
        value: int
        point_type: PointsTypeEnum

        def __init__(self, value: int, point_type: PointsTypeEnum) -> None:
            del value, point_type
            raise RuntimeError("fill_point_db runtime dependencies are not loaded")

    class CompetenceService:
        pass

    class LevelService:
        pass

    class PointsService:
        pass

    class UserCompetenceService:
        pass

    class UserService:
        pass


logger = loguru_logger


@dataclass(frozen=True, slots=True)
class RuntimeDependencies:
    """Application runtime dependencies required only for actual seed execution."""

    points_type_enum: type[PointsTypeEnum]
    role_enum: type[RoleEnum]
    level_model: type[Level]
    role_model: type[Role]
    setup_container: Callable[[], Awaitable[AsyncContainer]]
    adjust_user_points_dto_cls: type[AdjustUserPointsDTO]
    competence_create_dto_cls: type[CompetenceCreateDTO]
    competence_read_dto_cls: type[CompetenceReadDTO]
    user_create_dto_cls: type[UserCreateDTO]
    points_cls: type[Points]
    competence_service_cls: type[CompetenceService]
    level_service_cls: type[LevelService]
    points_service_cls: type[PointsService]
    user_competence_service_cls: type[UserCompetenceService]
    user_service_cls: type[UserService]


@lru_cache(maxsize=1)
def _get_runtime_dependencies() -> RuntimeDependencies:
    """Load and cache runtime-only application dependencies."""

    constants_module = import_module("src.pybot.core.constants")
    db_models_module = import_module("src.pybot.db.models")
    containers_module = import_module("src.pybot.di.containers")
    dto_module = import_module("src.pybot.dto")
    value_objects_module = import_module("src.pybot.dto.value_objects")
    services_module = import_module("src.pybot.services")

    return RuntimeDependencies(
        points_type_enum=constants_module.PointsTypeEnum,
        role_enum=constants_module.RoleEnum,
        level_model=db_models_module.Level,
        role_model=db_models_module.Role,
        setup_container=containers_module.setup_container,
        adjust_user_points_dto_cls=dto_module.AdjustUserPointsDTO,
        competence_create_dto_cls=dto_module.CompetenceCreateDTO,
        competence_read_dto_cls=dto_module.CompetenceReadDTO,
        user_create_dto_cls=dto_module.UserCreateDTO,
        points_cls=value_objects_module.Points,
        competence_service_cls=services_module.CompetenceService,
        level_service_cls=services_module.LevelService,
        points_service_cls=services_module.PointsService,
        user_competence_service_cls=services_module.UserCompetenceService,
        user_service_cls=services_module.UserService,
    )


@lru_cache(maxsize=1)
def _get_runtime_logger() -> Logger:
    """Create the configured application logger lazily for runtime execution."""

    logger_module = import_module("src.pybot.core.logger")
    return logger_module.setup_logger()


@dataclass(frozen=True, slots=True)
class CompetenceSeedConfig:
    """Seed payload for one competence entry.

    Attributes:
        name: Competence title to create or reuse.
        description: Human-readable competence description.
    """

    name: str
    description: str


class CompetencePreset(enum.StrEnum):
    """Named presets for competence seed payloads."""

    NONE = "none"
    PROFESSIONALS = "professionals"


_COMPETENCE_PRESETS: dict[CompetencePreset, tuple[CompetenceSeedConfig, ...]] = {
    CompetencePreset.NONE: (),
    CompetencePreset.PROFESSIONALS: (
        CompetenceSeedConfig("Python", "Разработка на Python"),
        CompetenceSeedConfig("SQL", "Работа с реляционными базами данных"),
        CompetenceSeedConfig("Git", "Контроль версий и командная разработка"),
        CompetenceSeedConfig("Linux", "Базовые навыки администрирования Linux"),
        CompetenceSeedConfig("Docker", "Контейнеризация приложений"),
        CompetenceSeedConfig("Algorithms", "Базовые алгоритмы и структуры данных"),
    ),
}

type CompetencePresetChoice = Literal["none", "professionals"]


@dataclass(frozen=True, slots=True)
class FillDatabaseConfig:
    """Configuration for database seed generation.

    Attributes:
        faker_locale: Locale used by Faker when generating users.
        num_fake_users: Number of test users to register.
        num_levels_per_type: Number of academic and reputation levels to create.
        max_points_range: Upper inclusive boundary for generated points.
        point_steps: Allowed point increments for generated values.
        min_telegram_id: Initial Telegram id for deterministic fake users.
        max_competencies_per_user: Upper bound of competencies per generated user.
        seed_points_reason: Reason stored in valuations created by seed points flow.
        seed_levels: Whether the script should seed levels.
        seed_roles: Whether the script should seed roles.
        seed_competencies: Whether the script should seed competences.
        seed_fake_users: Whether the script should seed fake users.
        competencies_preset: Named preset used when creating competences.
    """

    faker_locale: str = "ru_RU"
    num_fake_users: int = 50
    num_levels_per_type: int = 15
    max_points_range: int = 1_050
    point_steps: tuple[int, ...] = (5, 10)
    min_telegram_id: int = 1_000_000_000
    max_competencies_per_user: int = 3
    seed_points_reason: str = "Seed data bootstrap"
    seed_levels: bool = True
    seed_roles: bool = True
    seed_competencies: bool = True
    seed_fake_users: bool = True
    competencies_preset: CompetencePreset = CompetencePreset.PROFESSIONALS

    def __post_init__(self) -> None:
        """Validate seed parameters early.

        Raises:
            ValueError: If one of the numeric limits or point steps is invalid.
        """

        if self.num_fake_users < 0:
            raise ValueError("num_fake_users must be greater than or equal to 0")
        if self.num_levels_per_type < 0:
            raise ValueError("num_levels_per_type must be greater than or equal to 0")
        if self.max_points_range < 0:
            raise ValueError("max_points_range must be greater than or equal to 0")
        if self.min_telegram_id < 0:
            raise ValueError("min_telegram_id must be greater than or equal to 0")
        if self.max_competencies_per_user < 0:
            raise ValueError("max_competencies_per_user must be greater than or equal to 0")
        if not self.point_steps:
            raise ValueError("point_steps must contain at least one value")
        if any(step <= 0 for step in self.point_steps):
            raise ValueError("point_steps must contain only positive values")


@dataclass(frozen=True, slots=True)
class FillDatabaseCLIConfig:
    """Public CLI configuration for database seed generation.

    Attributes:
        faker_locale: Locale used by Faker when generating users.
        num_fake_users: Number of test users to register.
        num_levels_per_type: Number of academic and reputation levels to create.
        max_points_range: Upper inclusive boundary for generated points.
        point_steps: Allowed point increments for generated values.
        min_telegram_id: Initial Telegram id for deterministic fake users.
        max_competencies_per_user: Upper bound of competencies per generated user.
        seed_points_reason: Reason stored in valuations created by seed points flow.
        competencies_preset: Named preset used when creating competences.
        skip_levels: Whether to skip level seeding.
        skip_roles: Whether to skip role seeding.
        skip_competencies: Whether to skip competence seeding.
        skip_fake_users: Whether to skip fake-user seeding.
    """

    faker_locale: str = "ru_RU"
    num_fake_users: int = 50
    num_levels_per_type: int = 15
    max_points_range: int = 1_050
    point_steps: tuple[int, ...] = (5, 10)
    min_telegram_id: int = 1_000_000_000
    max_competencies_per_user: int = 3
    seed_points_reason: str = "Seed data bootstrap"
    competencies_preset: CompetencePresetChoice = "professionals"
    skip_levels: bool = False
    skip_roles: bool = False
    skip_competencies: bool = False
    skip_fake_users: bool = False


def build_seed_config(cli_config: FillDatabaseCLIConfig) -> FillDatabaseConfig:
    """Map CLI options into the internal runtime seed configuration.

    Args:
        cli_config: Public CLI configuration parsed by tyro.

    Returns:
        Internal runtime configuration for the async seed flow.
    """

    competencies_preset = CompetencePreset(cli_config.competencies_preset)

    return FillDatabaseConfig(
        faker_locale=cli_config.faker_locale,
        num_fake_users=cli_config.num_fake_users,
        num_levels_per_type=cli_config.num_levels_per_type,
        max_points_range=cli_config.max_points_range,
        point_steps=cli_config.point_steps,
        min_telegram_id=cli_config.min_telegram_id,
        max_competencies_per_user=cli_config.max_competencies_per_user,
        seed_points_reason=cli_config.seed_points_reason,
        seed_levels=not cli_config.skip_levels,
        seed_roles=not cli_config.skip_roles,
        seed_competencies=not cli_config.skip_competencies,
        seed_fake_users=not cli_config.skip_fake_users,
        competencies_preset=competencies_preset,
    )


def parse_cli_args(args: Sequence[str] | None = None) -> FillDatabaseCLIConfig:
    """Parse CLI arguments into the public tyro config.

    Args:
        args: Optional CLI arguments for testing or programmatic invocation.

    Returns:
        Parsed CLI configuration.
    """

    return tyro.cli(FillDatabaseCLIConfig, args=list(args) if args is not None else None)


def _get_competence_seed_entries(config: FillDatabaseConfig) -> tuple[CompetenceSeedConfig, ...]:
    """Resolve competence seed payloads for the selected preset.

    Args:
        config: Seed configuration.

    Returns:
        Competence entries mapped from the selected preset.
    """

    return _COMPETENCE_PRESETS[config.competencies_preset]


class PhoneNumberLength(enum.Enum):
    """Supported lengths for normalized phone values."""

    SHORTENED_FORMAT = 10
    AVERAGE_FORMAT = 11


class UserDataDict(TypedDict):
    """Generated user payload used by the seed script internals."""

    first_name: str
    last_name: str
    patronymic: str | None
    phone: str
    tg_id: int
    academic_points: int
    reputation_points: int
    competence_ids: list[int]


@dataclass(slots=True)
class UserGenerationState:
    """Mutable state for deterministic fake-user generation.

    Attributes:
        used_telegram_ids: Already reserved Telegram ids.
        used_phones: Already reserved phone numbers.
        current_telegram_id_seed: Current Telegram id counter.
    """

    used_telegram_ids: set[int]
    used_phones: set[str]
    current_telegram_id_seed: int


@dataclass(frozen=True, slots=True)
class SeedServices:
    """Service bundle used by helper steps during user seeding.

    Attributes:
        user_service: Service used to register users.
        user_competence_service: Service used to attach competences.
        points_service: Service used to seed points through gamification logic.
    """

    user_service: UserService
    user_competence_service: UserCompetenceService
    points_service: PointsService


def calculate_xp(n: int) -> int:
    """Calculate cumulative points required for a level.

    Args:
        n: Level number starting from 1.

    Returns:
        Required points for the requested level.
    """

    if n <= 0:
        return 0
    return 50 * n * (n - 1)


def _build_faker(config: FillDatabaseConfig) -> Faker:
    """Create a Faker instance for the provided seed config.

    Args:
        config: Seed configuration.

    Returns:
        Configured Faker instance.
    """

    return Faker(config.faker_locale)


async def generate_levels_data(
    session: AsyncSession,
    level_service: LevelService,
    config: FillDatabaseConfig,
) -> Sequence[Level]:
    """Seed academic and reputation levels.

    Args:
        session: Active database session.
        level_service: Service used to check existing levels.
        config: Seed configuration.

    Returns:
        Existing or newly created levels.
    """

    runtime = _get_runtime_dependencies()
    logger.info("Starting level generation")

    if await level_service.level_exists():
        logger.info("Levels already exist, skipping generation")
        return await level_service.find_all_levels()

    levels_to_add: list[Level] = []

    for level_num in range(1, config.num_levels_per_type + 1):
        required_xp = calculate_xp(level_num)

        levels_to_add.append(
            runtime.level_model(
                name=f"Уровень {level_num}",
                description=f"Требуется {required_xp} академических баллов для достижения этого уровня.",
                required_points=required_xp,
                level_type=runtime.points_type_enum.ACADEMIC,
            )
        )
        levels_to_add.append(
            runtime.level_model(
                name=f"Уровень {level_num}",
                description=f"Требуется {required_xp} репутационных баллов для достижения этого уровня.",
                required_points=required_xp,
                level_type=runtime.points_type_enum.REPUTATION,
            )
        )

    session.add_all(levels_to_add)
    await session.commit()
    logger.info("Added %s levels", len(levels_to_add))
    return levels_to_add


def _sanitize_phone_number(phone_raw: str, fake_data: Faker) -> str:
    """Normalize a Faker-generated phone number into E.164-like format.

    Args:
        phone_raw: Raw phone number from Faker.
        fake_data: Faker instance used for fallback generation.

    Returns:
        Sanitized phone number prefixed with `+`.
    """

    phone_cleaned = "".join(filter(str.isdigit, phone_raw))

    if phone_cleaned.startswith("8"):
        phone_cleaned = "7" + phone_cleaned[1:]
    elif len(phone_cleaned) == PhoneNumberLength.SHORTENED_FORMAT.value and not phone_cleaned.startswith("7"):
        phone_cleaned = "7" + phone_cleaned

    if len(phone_cleaned) > PhoneNumberLength.AVERAGE_FORMAT.value:
        phone_cleaned = phone_cleaned[-11:]

    if len(phone_cleaned) < PhoneNumberLength.SHORTENED_FORMAT.value:
        return "+" + "".join(filter(str.isdigit, fake_data.phone_number()))

    return "+" + phone_cleaned


async def generate_users_data(
    user_service: UserService,
    user_competence_service: UserCompetenceService,
    points_service: PointsService,
    competencies: Sequence[CompetenceReadDTO],
    config: FillDatabaseConfig,
) -> None:
    """Generate fake users and seed their gamification state.

    Args:
        user_service: Service used to register users and assign competences.
        points_service: Service used to seed points through business logic.
        competencies: Available competences that may be attached to users.
        config: Seed configuration.
    """

    logger.info("Starting generation of %s fake users", config.num_fake_users)

    fake_data = _build_faker(config)
    users_data = _generate_fake_users_data(competencies, config, fake_data)
    successfully_created = 0
    failed_count = 0
    created_users: list[tuple[int, UserDataDict]] = []

    for idx, user_data in enumerate(users_data, 1):
        try:
            user_id = await _register_seed_user(user_service, user_data, idx, len(users_data))
            if user_id is None:
                failed_count += 1
                continue

            created_users.append((user_id, user_data))
        except Exception as exc:
            failed_count += 1
            logger.error(
                "Failed to create user %s (%s %s): %s",
                idx,
                user_data["first_name"],
                user_data["last_name"],
                exc,
                exc_info=True,
            )

    created_user_ids = [user_id for user_id, _ in created_users]
    services = SeedServices(
        user_service=user_service,
        user_competence_service=user_competence_service,
        points_service=points_service,
    )
    for idx, (user_id, user_data) in enumerate(created_users, 1):
        try:
            await _seed_registered_user(
                services=services,
                created_user_ids=created_user_ids,
                user_id=user_id,
                user_data=user_data,
                config=config,
            )
            successfully_created += 1
            logger.debug("User %s seeded successfully (id=%s)", idx, user_id)
        except Exception as exc:
            failed_count += 1
            logger.error(
                "Failed to seed user %s (%s %s): %s",
                idx,
                user_data["first_name"],
                user_data["last_name"],
                exc,
                exc_info=True,
            )
    logger.success("Successfully created %s users. Errors: %s", successfully_created, failed_count)


def _generate_fake_users_data(
    competencies: Sequence[CompetenceReadDTO],
    config: FillDatabaseConfig,
    fake_data: Faker,
) -> list[UserDataDict]:
    """Create raw fake user payloads before registration.

    Args:
        competencies: Competences available for random assignment.
        config: Seed configuration.
        fake_data: Faker instance used for synthetic user data.

    Returns:
        User payloads ready to be passed into registration.
    """

    users_data: list[UserDataDict] = []
    state = UserGenerationState(
        used_telegram_ids=set(),
        used_phones=set(),
        current_telegram_id_seed=config.min_telegram_id,
    )

    for _ in range(config.num_fake_users):
        user_data, next_telegram_id_seed = _build_fake_user_data(
            competencies=competencies,
            state=state,
            config=config,
            fake_data=fake_data,
        )
        state.current_telegram_id_seed = next_telegram_id_seed
        users_data.append(user_data)

    return users_data


def _build_fake_user_data(
    *,
    competencies: Sequence[CompetenceReadDTO],
    state: UserGenerationState,
    config: FillDatabaseConfig,
    fake_data: Faker,
) -> tuple[UserDataDict, int]:
    """Build one fake user payload.

    Args:
        competencies: Competences available for random assignment.
        state: Mutable state used to avoid duplicate phones and Telegram ids.
        config: Seed configuration.
        fake_data: Faker instance used for synthetic user data.

    Returns:
        Tuple of generated user payload and next Telegram id seed.
    """

    first_name = fake_data.first_name()
    last_name = fake_data.last_name()
    patronymic = fake_data.middle_name() if fake_data.boolean(chance_of_getting_true=80) else None

    while state.current_telegram_id_seed in state.used_telegram_ids:
        state.current_telegram_id_seed += 1
    telegram_id = state.current_telegram_id_seed
    state.used_telegram_ids.add(telegram_id)
    next_telegram_id_seed = state.current_telegram_id_seed + 1

    phone_number = _sanitize_phone_number(fake_data.phone_number(), fake_data)
    if phone_number in state.used_phones:
        phone_number = _sanitize_phone_number(fake_data.phone_number(), fake_data)
    state.used_phones.add(phone_number)

    return (
        {
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic,
            "phone": phone_number,
            "tg_id": telegram_id,
            "academic_points": random.randrange(0, config.max_points_range + 1, random.choice(config.point_steps)),  # noqa: S311
            "reputation_points": random.randrange(0, config.max_points_range + 1, random.choice(config.point_steps)),  # noqa: S311
            "competence_ids": _pick_competence_ids(competencies, config),
        },
        next_telegram_id_seed,
    )


def _pick_competence_ids(
    competencies: Sequence[CompetenceReadDTO],
    config: FillDatabaseConfig,
) -> list[int]:
    """Pick a random subset of competences for a user.

    Args:
        competencies: Available competences.
        config: Seed configuration.

    Returns:
        Selected competence identifiers.
    """

    if not competencies or config.max_competencies_per_user == 0:
        return []

    selected_count = random.randint(1, min(config.max_competencies_per_user, len(competencies)))  # noqa: S311
    return random.sample([competence.id for competence in competencies], selected_count)


async def _register_seed_user(
    user_service: UserService,
    user_data: UserDataDict,
    idx: int,
    total_users: int,
) -> int | None:
    """Register one generated user through the application service.

    Args:
        user_service: Service used for student registration.
        user_data: Generated user payload.
        idx: Current user number for logging.
        total_users: Total number of generated users.

    Returns:
        Newly created user id or `None` if the created DTO does not contain it.
    """

    logger.debug(
        "Creating user %s/%s: %s %s",
        idx,
        total_users,
        user_data["first_name"],
        user_data["last_name"],
    )

    runtime = _get_runtime_dependencies()
    user = await user_service.register_student(
        runtime.user_create_dto_cls(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            patronymic=user_data["patronymic"],
            phone=user_data["phone"],
            tg_id=user_data["tg_id"],
        )
    )

    if not user.id:
        logger.error("User %s does not have an id after creation", idx)
        return None

    logger.debug("User %s registered successfully (id=%s)", idx, user.id)
    return user.id


async def _seed_registered_user(
    *,
    services: SeedServices,
    created_user_ids: Sequence[int],
    user_id: int,
    user_data: UserDataDict,
    config: FillDatabaseConfig,
) -> None:
    """Apply gamification data for a newly registered seed user.

    Args:
        services: Services used during seed user enrichment.
        created_user_ids: All successfully created user ids.
        user_id: Current user id.
        user_data: Generated user payload.
        config: Seed configuration.
    """

    runtime = _get_runtime_dependencies()
    giver_id = _select_seed_giver_id(created_user_ids, user_id)
    await _apply_seed_points(
        points_service=services.points_service,
        recipient_id=user_id,
        giver_id=giver_id,
        points=runtime.points_cls(
            value=user_data["academic_points"],
            point_type=runtime.points_type_enum.ACADEMIC,
        ),
        reason=config.seed_points_reason,
    )
    await _apply_seed_points(
        points_service=services.points_service,
        recipient_id=user_id,
        giver_id=giver_id,
        points=runtime.points_cls(
            value=user_data["reputation_points"],
            point_type=runtime.points_type_enum.REPUTATION,
        ),
        reason=config.seed_points_reason,
    )

    if user_data["competence_ids"]:
        await services.user_competence_service.add_user_competencies(user_id, user_data["competence_ids"])


def _select_seed_giver_id(created_user_ids: Sequence[int], recipient_id: int) -> int:
    """Choose a deterministic giver id for seed point operations.

    Args:
        created_user_ids: All registered user ids created during the seed run.
        recipient_id: User receiving the seed points.

    Returns:
        Identifier of the giver user.
    """

    if len(created_user_ids) <= 1:
        return recipient_id

    recipient_index = created_user_ids.index(recipient_id)
    return created_user_ids[(recipient_index + 1) % len(created_user_ids)]


async def _apply_seed_points(
    *,
    points_service: PointsService,
    recipient_id: int,
    giver_id: int,
    points: Points,
    reason: str,
) -> None:
    """Apply one points adjustment through the real points service.

    Args:
        points_service: Service responsible for gamification point updates.
        recipient_id: User receiving the points.
        giver_id: User acting as the points giver.
        points: Points value object to apply.
        reason: Reason stored with the seeded valuation.
    """

    if points.value == 0:
        return

    runtime = _get_runtime_dependencies()
    await points_service.change_points(
        runtime.adjust_user_points_dto_cls(
            recipient_id=recipient_id,
            giver_id=giver_id,
            points=points,
            reason=reason,
        )
    )


async def get_all_roles(session: AsyncSession) -> Sequence[Role]:
    """Fetch all roles from the database.

    Args:
        session: Active database session.

    Returns:
        Stored role entities.
    """

    runtime = _get_runtime_dependencies()
    stmt = select(runtime.role_model)
    result = await session.execute(stmt)
    return result.scalars().all()


async def role_exists(session: AsyncSession) -> bool:
    """Check whether at least one role already exists.

    Args:
        session: Active database session.

    Returns:
        `True` when roles are already present in the database.
    """

    runtime = _get_runtime_dependencies()
    stmt = select(runtime.role_model).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def add_roles_data(session: AsyncSession) -> Sequence[Role]:
    """Seed system roles if they are absent.

    Args:
        session: Active database session.

    Returns:
        Existing or newly created role entities.
    """

    runtime = _get_runtime_dependencies()
    logger.info("Starting role generation")

    if await role_exists(session):
        logger.info("Roles already exist, skipping generation")
        return await get_all_roles(session)

    roles_to_add = [runtime.role_model(name=role_obj.value) for role_obj in runtime.role_enum]
    session.add_all(roles_to_add)
    await session.commit()
    logger.info("Added %s roles", len(roles_to_add))
    return roles_to_add


async def add_competencies_data(
    competence_service: CompetenceService,
    config: FillDatabaseConfig,
) -> Sequence[CompetenceReadDTO]:
    """Seed competences if they are absent.

    Args:
        competence_service: Service used to create competences.
        config: Seed configuration.

    Returns:
        Existing or newly created competence DTOs.
    """

    runtime = _get_runtime_dependencies()
    logger.info("Starting competence generation")

    existing = await competence_service.find_all_competencies()
    if existing:
        logger.info("Competencies already exist, skipping generation")
        return existing

    competencies_seed = _get_competence_seed_entries(config)
    if not competencies_seed:
        logger.info("Competence preset %s is empty, skipping generation", config.competencies_preset)
        return []

    created: list[CompetenceReadDTO] = []
    for competence in competencies_seed:
        created.append(
            await competence_service.create_competence(
                runtime.competence_create_dto_cls(name=competence.name, description=competence.description)
            )
        )

    logger.info("Added %s competencies", len(created))
    return created


async def fill_database(config: FillDatabaseConfig | None = None) -> None:
    """Run the database seed process.

    Args:
        config: Optional seed configuration. Defaults to the standard script
            behavior when omitted.
    """

    _ensure_project_root_on_path()
    runtime = _get_runtime_dependencies()
    runtime_logger = _get_runtime_logger()
    seed_config = config or FillDatabaseConfig()
    runtime_logger.info("Starting database seed script")

    container = await runtime.setup_container()
    try:
        async with container() as request_container:
            session = await request_container.get(AsyncSession)
            competence_service = await request_container.get(runtime.competence_service_cls)
            level_service = await request_container.get(runtime.level_service_cls)
            points_service = await request_container.get(runtime.points_service_cls)
            user_competence_service = await request_container.get(runtime.user_competence_service_cls)
            user_service = await request_container.get(runtime.user_service_cls)

            try:
                competencies: Sequence[CompetenceReadDTO] = []

                if seed_config.seed_levels:
                    await generate_levels_data(session, level_service, seed_config)
                else:
                    runtime_logger.info("Skipping level generation by config")

                if seed_config.seed_roles:
                    await add_roles_data(session)
                else:
                    runtime_logger.info("Skipping role generation by config")

                if seed_config.seed_competencies:
                    competencies = await add_competencies_data(competence_service, seed_config)
                else:
                    runtime_logger.info("Skipping competence generation by config")

                if seed_config.seed_fake_users:
                    await generate_users_data(
                        user_service,
                        user_competence_service,
                        points_service,
                        competencies,
                        seed_config,
                    )
                else:
                    runtime_logger.info("Skipping fake user generation by config")

                runtime_logger.success("Database seeding finished successfully")
            except Exception as exc:
                await session.rollback()
                runtime_logger.error("Database seeding failed: %s", exc, exc_info=True)
                runtime_logger.warning("Database seeding was rolled back")
    finally:
        await container.close()


def _ensure_project_root_on_path() -> None:
    """Ensure the repository root is available in `sys.path` for script runs."""

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def main(cli_config: FillDatabaseCLIConfig | None = None) -> None:
    """Run the seed script from a synchronous tyro-powered entrypoint.

    Args:
        cli_config: Optional CLI configuration for programmatic invocation.
    """

    resolved_cli_config = cli_config or parse_cli_args()
    _ensure_project_root_on_path()
    asyncio.run(fill_database(build_seed_config(resolved_cli_config)))


if __name__ == "__main__":
    main()
