import re
from enum import Enum


class PhoneConstants(Enum):
    NumberLengthWithCountryCode = 11
    NumberLengthWithoutCountryCode = 10


async def normalize_phone(phone_raw: str) -> str:
    """
    Приводит номер к виду +7XXXXXXXXXX.
    Если номер некорректный — кидает ValueError.
    """

    # оставляем только цифры
    digits = re.sub(r"\D", "", phone_raw)

    # вариант 1: уже с «8» или «7» и 11 цифр
    if len(digits) == PhoneConstants.NumberLengthWithCountryCode and digits[0] in {"7", "8"}:
        digits = "7" + digits[1:]  # заменяем первую цифру на 7
    # вариант 2: 10 цифр (без кода страны)
    elif len(digits) == PhoneConstants.NumberLengthWithoutCountryCode:
        digits = "7" + digits
    else:
        raise ValueError(f"Некорректный номер телефона: {phone_raw!r}")

    return f"+{digits}"
