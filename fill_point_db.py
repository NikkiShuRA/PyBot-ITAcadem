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

from src.pybot import create_user_profile, update_user_points_by_id
from src.pybot.core.constants import PointsTypeEnum
from src.pybot.core.logger import setup_logger
from src.pybot.db.database import SessionLocal, engine
from src.pybot.db.models import Level
from src.pybot.dto import UserCreateDTO

logger = setup_logger()
fake = Faker("ru_RU")

# --- Конфигурация скрипта ---
NUM_FAKE_USERS = 5
NUM_LEVELS_PER_TYPE = 15
MAX_POINTS_RANGE = 1050
POINT_STEPS = [5, 10]
MIN_TELEGRAM_ID = 1000000000


class PhoneNumberLength(enum.Enum):
    SHORTENED_FORMAT = 10
    AVERAGE_FORMAT = 11


class UserDataDict(TypedDict):
    """Типизированный словарь для данных пользователя"""

    first_name: str
    last_name: str
    patronymic: str | None
    phone: str
    tg_id: int
    academic_points: int
    reputation_points: int


async def level_exists(session: AsyncSession) -> bool:
    """Проверяет, существуют ли уровни в базе данных."""
    stmt = select(Level).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def get_all_levels(session: AsyncSession) -> Sequence[Level]:
    """Получает все уровни из базы данных."""
    stmt = select(Level)
    result = await session.execute(stmt)
    return result.scalars().all()


def calculate_xp(n: int) -> int:
    """Рассчитывает необходимое количество опыта (XP) для уровня N."""
    if n <= 0:
        return 0
    return 50 * n * (n - 1)


async def generate_levels_data(session: AsyncSession) -> Sequence[Level]:
    """Генерирует и добавляет уровни в БД (если их там еще нет)."""
    logger.info("Начинаем генерацию уровней...")

    if await level_exists(session):
        logger.info("Уровни уже существуют в БД. Пропускаем генерацию.")
        return await get_all_levels(session)

    levels_to_add = []

    for level_num in range(1, NUM_LEVELS_PER_TYPE + 1):
        required_xp = calculate_xp(level_num)

        academic_level = Level(
            name=f"Академический Уровень {level_num}",
            description=f"Требуется {required_xp} академических баллов для достижения этого уровня.",
            required_points=required_xp,
            level_type=PointsTypeEnum.ACADEMIC,
        )
        levels_to_add.append(academic_level)

        reputation_level = Level(
            name=f"Репутационный Уровень {level_num}",
            description=f"Требуется {required_xp} репутационных баллов для достижения этого уровня.",
            required_points=required_xp,
            level_type=PointsTypeEnum.REPUTATION,
        )
        levels_to_add.append(reputation_level)

    session.add_all(levels_to_add)
    await session.commit()
    logger.info(f"Сгенерировано и добавлено {len(levels_to_add)} уровней в базу данных.")

    return levels_to_add


def _sanitize_phone_number(phone_raw: str) -> str:
    """Преобразует телефонный номер в стандартный формат."""
    phone_cleaned: str = "".join(filter(str.isdigit, phone_raw))

    if phone_cleaned.startswith("8"):
        phone_cleaned = "7" + phone_cleaned[1:]
    elif len(phone_cleaned) == PhoneNumberLength.SHORTENED_FORMAT.value and not phone_cleaned.startswith("7"):
        phone_cleaned = "7" + phone_cleaned

    if len(phone_cleaned) > int(PhoneNumberLength.AVERAGE_FORMAT.value):
        phone_cleaned = phone_cleaned[-11:]

    # Если номер слишком короткий, берём новый из генератора
    if len(phone_cleaned) < int(PhoneNumberLength.SHORTENED_FORMAT.value):
        return "+" + "".join(filter(str.isdigit, fake.phone_number()))

    return "+" + phone_cleaned


async def generate_users_data(session: AsyncSession, num_users: int) -> None:
    """Генерирует и добавляет фейковых пользователей в базу данных."""
    logger.info(f"Начинаем генерацию {num_users} фейковых пользователей...")

    users_data: list[UserDataDict] = []
    used_telegram_ids: set[int] = set()
    used_phones: set[str] = set()
    current_telegram_id_seed = MIN_TELEGRAM_ID

    # Шаг 1: Подготавливаем данные
    for _ in range(num_users):
        first_name: str = fake.first_name()
        last_name: str = fake.last_name()
        patronymic: str | None = fake.middle_name() if fake.boolean(chance_of_getting_true=80) else None

        # Генерируем уникальный Telegram ID
        while current_telegram_id_seed in used_telegram_ids:
            current_telegram_id_seed += 1
        telegram_id: int = current_telegram_id_seed
        used_telegram_ids.add(telegram_id)
        current_telegram_id_seed += 1

        # Генерируем и нормализуем телефон
        phone_number: str = _sanitize_phone_number(fake.phone_number())

        # Проверка уникальности телефона
        if phone_number in used_phones:
            phone_number = _sanitize_phone_number(fake.phone_number())

        used_phones.add(phone_number)

        academic_points: int = random.randrange(  # noqa: S311
            0,
            MAX_POINTS_RANGE + 1,
            random.choice(POINT_STEPS),  # noqa: S311
        )
        reputation_points: int = random.randrange(  # noqa: S311
            0,
            MAX_POINTS_RANGE + 1,
            random.choice(POINT_STEPS),  # noqa: S311
        )

        user_entry: UserDataDict = {
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic,
            "phone": phone_number,
            "tg_id": telegram_id,
            "academic_points": academic_points,
            "reputation_points": reputation_points,
        }
        users_data.append(user_entry)

    # Шаг 2: Создаём пользователей с обработкой ошибок
    successfully_created = 0
    failed_count = 0

    for idx, user_data in enumerate(users_data, 1):
        try:
            logger.debug(
                f"Создание пользователя {idx}/{len(users_data)}: {user_data['first_name']} {user_data['last_name']}"
            )

            user = await create_user_profile(
                db=session,
                data=UserCreateDTO(
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    patronymic=user_data["patronymic"],
                    phone=user_data["phone"],
                    tg_id=user_data["tg_id"],
                ),
            )

            if not user or not user.id:
                logger.error(f"Пользователь {idx} не имеет ID после создания")
                failed_count += 1
                continue

            # Обновляем баллы
            await update_user_points_by_id(
                db=session,
                user_id=user.id,
                points_value=user_data["academic_points"],
                points_type=PointsTypeEnum.ACADEMIC,
            )

            await update_user_points_by_id(
                db=session,
                user_id=user.id,
                points_value=user_data["reputation_points"],
                points_type=PointsTypeEnum.REPUTATION,
            )

            successfully_created += 1
            logger.debug(f"✓ Пользователь {idx} успешно создан (ID: {user.id})")

        except Exception as e:
            failed_count += 1
            logger.error(
                f"✗ Ошибка при создании пользователя {idx} ({user_data['first_name']} {user_data['last_name']}): {e}",
                exc_info=True,
            )
            continue

    await session.commit()
    logger.success(f"Успешно создано {successfully_created} пользователей. Ошибок: {failed_count}")


async def fill_database() -> None:
    """Основная функция для заполнения базы данных фейковыми данными."""
    logger.info("Запуск скрипта заполнения базы данных...")

    async with SessionLocal() as session:
        try:
            # 1️⃣ Генерация и добавление уровней
            await generate_levels_data(session)

            # 2️⃣ Генерация и добавление пользователей
            await generate_users_data(session, NUM_FAKE_USERS)

            logger.success("Заполнение базы данных успешно завершено!")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка во время заполнения базы данных: {e}", exc_info=True)
            logger.warning("Заполнение базы данных было отменено (rollback).")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    # Устанавливаем корректный путь для импорта
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    asyncio.run(fill_database())
