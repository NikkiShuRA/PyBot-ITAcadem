import phonenumbers


def normalize_phone(phone: str) -> str:
    try:
        parsed = phonenumbers.parse(phone)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)  # +1234567890
    except phonenumbers.NumberParseException as err:
        raise ValueError("Некорректный номер телефона") from err
