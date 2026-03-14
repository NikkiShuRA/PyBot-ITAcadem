import asyncio
import enum
import os
import random
import sys
from collections.abc import Sequence
from typing import TypedDict

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.pybot.core.constants import LevelTypeEnum, RoleEnum
from src.pybot.core.logger import setup_logger
from src.pybot.db.models import Level, Role
from src.pybot.di.containers import setup_container
from src.pybot.dto import AdjustUserPointsDTO, CompetenceCreateDTO, CompetenceReadDTO, UserCreateDTO
from src.pybot.dto.value_objects import Points
from src.pybot.services.competence import CompetenceService
from src.pybot.services.levels import LevelService
from src.pybot.services.points import PointsService
from src.pybot.services.users import UserService

logger = setup_logger()
fake = Faker("ru_RU")

NUM_FAKE_USERS = 50
NUM_LEVELS_PER_TYPE = 15
MAX_POINTS_RANGE = 1050
POINT_STEPS = [5, 10]
MIN_TELEGRAM_ID = 1000000000
MAX_COMPETENCIES_PER_USER = 3
SEED_POINTS_REASON = "Seed data bootstrap"
COMPETENCIES_SEED: tuple[tuple[str, str], ...] = (
    ("Python", "Разработка на Python"),
    ("SQL", "Работа с реляционными базами данных"),
    ("Git", "Контроль версий и командная разработка"),
    ("Linux", "Базовые навыки администрирования Linux"),
    ("Docker", "Контейнеризация приложений"),
    ("Algorithms", "Базовые алгоритмы и структуры данных"),
)


class PhoneNumberLength(enum.Enum):
    SHORTENED_FORMAT = 10
    AVERAGE_FORMAT = 11


class UserDataDict(TypedDict):
    first_name: str
    last_name: str
    patronymic: str | None
    phone: str
    tg_id: int
    academic_points: int
    reputation_points: int
    competence_ids: list[int]


def calculate_xp(n: int) -> int:
    if n <= 0:
        return 0
    return 50 * n * (n - 1)


async def generate_levels_data(session: AsyncSession, level_service: LevelService) -> Sequence[Level]:
    logger.info("Starting level generation")

    if await level_service.level_exists():
        logger.info("Levels already exist, skipping generation")
        return await level_service.find_all_levels()

    levels_to_add: list[Level] = []

    for level_num in range(1, NUM_LEVELS_PER_TYPE + 1):
        required_xp = calculate_xp(level_num)

        levels_to_add.append(
            Level(
                name=f"Уровень {level_num}",
                description=f"Требуется {required_xp} академических баллов для достижения этого уровня.",
                required_points=required_xp,
                level_type=LevelTypeEnum.ACADEMIC,
            )
        )
        levels_to_add.append(
            Level(
                name=f"Уровень {level_num}",
                description=f"Требуется {required_xp} репутационных баллов для достижения этого уровня.",
                required_points=required_xp,
                level_type=LevelTypeEnum.REPUTATION,
            )
        )

    session.add_all(levels_to_add)
    await session.commit()
    logger.info("Added %s levels", len(levels_to_add))
    return levels_to_add


def _sanitize_phone_number(phone_raw: str) -> str:
    phone_cleaned = "".join(filter(str.isdigit, phone_raw))

    if phone_cleaned.startswith("8"):
        phone_cleaned = "7" + phone_cleaned[1:]
    elif len(phone_cleaned) == PhoneNumberLength.SHORTENED_FORMAT.value and not phone_cleaned.startswith("7"):
        phone_cleaned = "7" + phone_cleaned

    if len(phone_cleaned) > PhoneNumberLength.AVERAGE_FORMAT.value:
        phone_cleaned = phone_cleaned[-11:]

    if len(phone_cleaned) < PhoneNumberLength.SHORTENED_FORMAT.value:
        return "+" + "".join(filter(str.isdigit, fake.phone_number()))

    return "+" + phone_cleaned


async def generate_users_data(
    user_service: UserService,
    points_service: PointsService,
    competencies: Sequence[CompetenceReadDTO],
    num_users: int,
) -> None:
    logger.info("Starting generation of %s fake users", num_users)

    users_data = _generate_fake_users_data(competencies, num_users)
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
    for idx, (user_id, user_data) in enumerate(created_users, 1):
        try:
            await _seed_registered_user(
                user_service=user_service,
                points_service=points_service,
                created_user_ids=created_user_ids,
                user_id=user_id,
                user_data=user_data,
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


def _generate_fake_users_data(competencies: Sequence[CompetenceReadDTO], num_users: int) -> list[UserDataDict]:
    users_data: list[UserDataDict] = []
    used_telegram_ids: set[int] = set()
    used_phones: set[str] = set()
    current_telegram_id_seed = MIN_TELEGRAM_ID

    for _ in range(num_users):
        user_data, current_telegram_id_seed = _build_fake_user_data(
            competencies=competencies,
            used_telegram_ids=used_telegram_ids,
            used_phones=used_phones,
            current_telegram_id_seed=current_telegram_id_seed,
        )
        users_data.append(user_data)

    return users_data


def _build_fake_user_data(
    *,
    competencies: Sequence[CompetenceReadDTO],
    used_telegram_ids: set[int],
    used_phones: set[str],
    current_telegram_id_seed: int,
) -> tuple[UserDataDict, int]:
    first_name = fake.first_name()
    last_name = fake.last_name()
    patronymic = fake.middle_name() if fake.boolean(chance_of_getting_true=80) else None

    while current_telegram_id_seed in used_telegram_ids:
        current_telegram_id_seed += 1
    telegram_id = current_telegram_id_seed
    used_telegram_ids.add(telegram_id)
    next_telegram_id_seed = current_telegram_id_seed + 1

    phone_number = _sanitize_phone_number(fake.phone_number())
    if phone_number in used_phones:
        phone_number = _sanitize_phone_number(fake.phone_number())
    used_phones.add(phone_number)

    return (
        {
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic,
            "phone": phone_number,
            "tg_id": telegram_id,
            "academic_points": random.randrange(0, MAX_POINTS_RANGE + 1, random.choice(POINT_STEPS)),  # noqa: S311
            "reputation_points": random.randrange(0, MAX_POINTS_RANGE + 1, random.choice(POINT_STEPS)),  # noqa: S311
            "competence_ids": _pick_competence_ids(competencies),
        },
        next_telegram_id_seed,
    )


def _pick_competence_ids(competencies: Sequence[CompetenceReadDTO]) -> list[int]:
    if not competencies:
        return []

    selected_count = random.randint(1, min(MAX_COMPETENCIES_PER_USER, len(competencies)))  # noqa: S311
    return random.sample([competence.id for competence in competencies], selected_count)


async def _register_seed_user(
    user_service: UserService,
    user_data: UserDataDict,
    idx: int,
    total_users: int,
) -> int | None:
    logger.debug(
        "Creating user %s/%s: %s %s",
        idx,
        total_users,
        user_data["first_name"],
        user_data["last_name"],
    )

    user = await user_service.register_student(
        UserCreateDTO(
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
    user_service: UserService,
    points_service: PointsService,
    created_user_ids: Sequence[int],
    user_id: int,
    user_data: UserDataDict,
) -> None:
    giver_id = _select_seed_giver_id(created_user_ids, user_id)
    await _apply_seed_points(
        points_service=points_service,
        recipient_id=user_id,
        giver_id=giver_id,
        points_value=user_data["academic_points"],
        points_type=LevelTypeEnum.ACADEMIC,
    )
    await _apply_seed_points(
        points_service=points_service,
        recipient_id=user_id,
        giver_id=giver_id,
        points_value=user_data["reputation_points"],
        points_type=LevelTypeEnum.REPUTATION,
    )

    if user_data["competence_ids"]:
        await user_service.add_user_competencies(user_id, user_data["competence_ids"])


def _select_seed_giver_id(created_user_ids: Sequence[int], recipient_id: int) -> int:
    if len(created_user_ids) <= 1:
        return recipient_id

    recipient_index = created_user_ids.index(recipient_id)
    return created_user_ids[(recipient_index + 1) % len(created_user_ids)]


async def _apply_seed_points(
    *,
    points_service: PointsService,
    recipient_id: int,
    giver_id: int,
    points_value: int,
    points_type: LevelTypeEnum,
) -> None:
    if points_value == 0:
        return

    await points_service.change_points(
        AdjustUserPointsDTO(
            recipient_id=recipient_id,
            giver_id=giver_id,
            points=Points(value=points_value, point_type=points_type),
            reason=SEED_POINTS_REASON,
        )
    )


async def get_all_roles(session: AsyncSession) -> Sequence[Role]:
    stmt = select(Role)
    result = await session.execute(stmt)
    return result.scalars().all()


async def role_exists(session: AsyncSession) -> bool:
    stmt = select(Role).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def add_roles_data(session: AsyncSession) -> Sequence[Role]:
    logger.info("Starting role generation")

    if await role_exists(session):
        logger.info("Roles already exist, skipping generation")
        return await get_all_roles(session)

    roles_to_add = [Role(name=role_obj.value) for role_obj in RoleEnum]
    session.add_all(roles_to_add)
    await session.commit()
    logger.info("Added %s roles", len(roles_to_add))
    return roles_to_add


async def add_competencies_data(competence_service: CompetenceService) -> Sequence[CompetenceReadDTO]:
    logger.info("Starting competence generation")

    existing = await competence_service.get_all_competencies()
    if existing:
        logger.info("Competencies already exist, skipping generation")
        return existing

    created: list[CompetenceReadDTO] = []
    for name, description in COMPETENCIES_SEED:
        created.append(
            await competence_service.create_competence(CompetenceCreateDTO(name=name, description=description))
        )

    logger.info("Added %s competencies", len(created))
    return created


async def fill_database() -> None:
    logger.info("Starting database seed script")

    container = await setup_container()
    try:
        async with container() as request_container:
            session = await request_container.get(AsyncSession)
            competence_service = await request_container.get(CompetenceService)
            level_service = await request_container.get(LevelService)
            points_service = await request_container.get(PointsService)
            user_service = await request_container.get(UserService)

            try:
                await generate_levels_data(session, level_service)
                await add_roles_data(session)
                competencies = await add_competencies_data(competence_service)
                await generate_users_data(user_service, points_service, competencies, NUM_FAKE_USERS)
                logger.success("Database seeding finished successfully")
            except Exception as exc:
                await session.rollback()
                logger.error("Database seeding failed: %s", exc, exc_info=True)
                logger.warning("Database seeding was rolled back")
    finally:
        await container.close()


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    asyncio.run(fill_database())
