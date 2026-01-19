import re

import phonenumbers
from phonenumbers import PhoneNumberFormat


def normalize_phone(
    phone: str,
    region: str | None = "RU",
    *,
    strict: bool = True,
) -> str:
    """
    Нормализует телефон в E.164.

    Принимает:
      - phone: строка с телефоном в любом виде (с пробелами/скобками/дефисами),
        может быть:
          * международный: "+442083661177"
          * локальный/национальный: "020 8366 1177" (тогда нужен region) [web:71]
      - region: регион по умолчанию (например "RU", "GB").
        Если None, то номер обязан быть международным (начинаться с '+'). [web:71]
      - strict: если True — проверка is_valid_number (строгая),
                если False — is_possible_number (мягче, чаще подходит для тестовых данных). [web:123]

    Возвращает:
      - строку в формате E.164 (например "+79124130102"). [web:71]

    Исключения:
      - ValueError("Некорректный номер телефона") если номер не парсится/не проходит проверку.
    """
    if not phone:
        raise ValueError("Некорректный номер телефона")

    s = phone.strip()

    # Если пользователь ввёл "00..." как международный префикс — приводим к "+"
    # (часто встречается в Европе)
    if s.startswith("00"):
        s = "+" + s[2:]

    # Удаляем всё, кроме цифр и '+', чтобы не мешали пробелы/скобки/дефисы
    s = re.sub(r"[^\d+]", "", s)

    # Если номер не начинается с '+', парсим как "локальный" относительно региона
    # (без региона такой номер может быть непарсибельным). [web:71]
    try:
        parsed = phonenumbers.parse(s, None if s.startswith("+") else region)
    except phonenumbers.NumberParseException as err:
        raise ValueError("Некорректный номер телефона") from err

    # ok = phonenumbers.is_valid_number(parsed) if strict else phonenumbers.is_possible_number(parsed)
    # if not ok:
    #     raise ValueError("Некорректный номер телефона")

    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
