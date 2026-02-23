import pytest
from pybot.utils.phonenumber_normalization import normalize_phone


class TestNormalizePhoneRU:
    """Тесты только для русских номеров."""

    def test_e164_format(self) -> None:
        """E.164 формат +7..."""
        assert normalize_phone("+79124130102") == "+79124130102"

    def test_local_format_8(self) -> None:
        """Локальный формат с 8."""
        assert normalize_phone("89124130102") == "+79124130102"

    def test_with_formatting(self) -> None:
        """С пробелами и скобками."""
        assert normalize_phone("+7 (912) 413-01-02") == "+79124130102"
        assert normalize_phone("8 (912) 413-01-02") == "+79124130102"

    def test_non_russian_rejected(self) -> None:
        """Английский номер отклоняется."""
        with pytest.raises(ValueError):
            normalize_phone("+442083661177")

        with pytest.raises(ValueError):
            normalize_phone("+1 201-555-0123")

    def test_invalid_russian(self) -> None:
        """Невалидный русский номер."""
        with pytest.raises(ValueError):
            normalize_phone("+7912413")  # Слишком короткий

        with pytest.raises(ValueError):
            normalize_phone("89")  # Слишком короткий

    def test_with_leading_plus_and_country_code(self) -> None:
        """Номер с +7 уже в начале."""
        assert normalize_phone("+79876543210", strict=False) == "+79876543210"

    def test_empty_and_whitespace(self) -> None:
        """Пустой номер и только пробелы."""
        with pytest.raises(ValueError):
            normalize_phone("")

        with pytest.raises(ValueError):
            normalize_phone("   ")

        with pytest.raises(ValueError):
            normalize_phone(None)

    def test_non_strict_mode(self) -> None:
        """В non-strict режиме возможны номера."""
        # Работает в режиме is_possible_number
        result = normalize_phone("79124130102", strict=False)
        assert result == "+79124130102"
