import re

import phonenumbers
from phonenumbers import PhoneNumberFormat

NUMBER_LENGTH = 11
PHONE_CODE = 7
MIN_PHONE_LENGTH = 10
MAX_PHONE_LENGTH = 15


def normalize_phone(phone: str, strict: bool = True) -> str:
    """
    Нормализует телефон РФ в E.164 (+79XXXXXXXXX).

    Args:
        phone: Номер в любом формате (+7..., 8..., с пробелами, скобками)
        strict: True - полная валидация, False - проверка только структуры

    Returns:
        str: Номер в формате +79XXXXXXXXX

    Raises:
        ValueError: Если номер не валиден или не из РФ

    Примеры:
        >>> normalize_phone("+79876543210")
        '+79876543210'
        >>> normalize_phone("89876543210")
        '+79876543210'
        >>> normalize_phone("+7 (987) 654-32-10")
        '+79876543210'
    """
    if not phone or not phone.strip():
        raise ValueError("Некорректный номер телефона")

    s = phone.strip()

    # Удаляем всё, кроме цифр и '+'
    s = re.sub(r"[^\d+]", "", s)

    if not s:
        raise ValueError("Некорректный номер телефона")

    # Валидация длины
    if len(s) < MIN_PHONE_LENGTH or len(s) > MAX_PHONE_LENGTH:
        raise ValueError("Некорректный номер телефона")

    # Если номер начинается с 8 (локальный РФ) -> конвертируем в +7
    if s.startswith("8") and len(s) == NUMBER_LENGTH:
        s = "+7" + s[1:]

    try:
        parsed = phonenumbers.parse(s, "RU")
    except phonenumbers.NumberParseException as err:
        raise ValueError("Некорректный номер телефона") from err

    # Выбираем режим валидации
    is_valid = phonenumbers.is_valid_number(parsed) if strict else phonenumbers.is_possible_number(parsed)

    if not is_valid:
        raise ValueError("Некорректный номер телефона")

    # ✅ ТОЛЬКО проверяем что это РФ номер
    if parsed.country_code != PHONE_CODE:
        raise ValueError("Некорректный номер телефона")

    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
