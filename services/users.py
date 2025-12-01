# services/users.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db_class.models import User
import re

async def normalize_phone(phone_raw: str) -> str:
    """
    Приводит номер к виду +7XXXXXXXXXX.
    Если номер некорректный — кидает ValueError.
    """

    # оставляем только цифры
    digits = re.sub(r"\D", "", phone_raw)

    # вариант 1: уже с «8» или «7» и 11 цифр
    if len(digits) == 11 and digits[0] in ("7", "8"):
        digits = "7" + digits[1:]  # заменяем первую цифру на 7
    # вариант 2: 10 цифр (без кода страны)
    elif len(digits) == 10:
        digits = "7" + digits
    else:
        raise ValueError(f"Некорректный номер телефона: {phone_raw!r}")

    return f"+{digits}"


async def get_user_by_telegram_id(
    db: AsyncSession,
    tg_id: int,
) -> User | None:
    result = await db.execute(
        select(User).where(User.telegram_id == tg_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    res = await db.execute(select(User).where(User.phone_number == phone))
    return res.scalar_one_or_none()


async def attach_telegram_to_user(db: AsyncSession, user: User, tg_id: int) -> User:
    if user.telegram_id != tg_id:
        user.telegram_id = tg_id
        await db.commit()
        await db.refresh(user)
    return user


async def create_user_profile(
    db: AsyncSession,
    *,
    phone: str,
    tg_id: int,
    first_name: str,
    last_name: str | None = None,
    patronymic: str | None = None,
) -> User:
    user = User(
        phone_number=phone,
        telegram_id=tg_id,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
