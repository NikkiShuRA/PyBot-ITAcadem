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

    def test_rejects_string_that_becomes_empty_after_cleanup(self) -> None:
        """Номер из шума должен падать после очистки, а не тихо проходить дальше."""
        with pytest.raises(ValueError):
            normalize_phone("() -")

    def test_non_strict_mode(self) -> None:
        """В non-strict режиме возможны номера."""
        # Работает в режиме is_possible_number
        result = normalize_phone("79124130102", strict=False)
        assert result == "+79124130102"

    def test_parse_error_is_mapped_to_value_error(self) -> None:
        """Некачественный ввод с формально подходящей длиной должен маппиться в единый ValueError."""
        with pytest.raises(ValueError):
            normalize_phone("+7+9124130102")

    def test_strict_mode_rejects_structurally_correct_but_invalid_number(self) -> None:
        """Строгий режим должен отбрасывать номер, который парсится, но не считается валидным."""
        with pytest.raises(ValueError):
            normalize_phone("70000000000", strict=True)

    def test_repeated_calls_use_lru_cache(self) -> None:
        normalize_phone.cache_clear()

        first = normalize_phone("+79124130102")
        second = normalize_phone("+79124130102")
        cache_info = normalize_phone.cache_info()

        assert first == second == "+79124130102"
        assert cache_info.hits == 1
        assert cache_info.misses == 1
