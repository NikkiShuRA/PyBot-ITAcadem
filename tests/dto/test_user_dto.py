import pytest

from pybot.dto import UserCreateDTO
from pybot.domain.exceptions import NameInputValidationError


def test_validate_name_input_returns_clean_value_for_valid_name() -> None:
    result = UserCreateDTO.validate_name_input("  Иван  ")

    assert result == "Иван"


def test_validate_name_input_rejects_invalid_symbols() -> None:
    with pytest.raises(NameInputValidationError) as exc_info:
        UserCreateDTO.validate_name_input("Иван123")

    assert exc_info.value.reason == "invalid_symbols"


def test_validate_name_input_returns_none_for_empty_optional_value() -> None:
    result = UserCreateDTO.validate_name_input("   ", allow_empty=True)

    assert result is None


def test_validate_name_input_rejects_too_long_name() -> None:
    with pytest.raises(NameInputValidationError) as exc_info:
        UserCreateDTO.validate_name_input("И" * (UserCreateDTO.NAME_MAX_LENGTH + 1))

    assert exc_info.value.reason == "too_long"
    assert exc_info.value.max_length == UserCreateDTO.NAME_MAX_LENGTH
