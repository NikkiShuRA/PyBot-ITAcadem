import pytest

from pybot.utils.normalize_message import _normalize_message_cached, normalize_message


def test_normalize_message_trims_text() -> None:
    _normalize_message_cached.cache_clear()

    assert normalize_message("  hello  ", max_length=10) == "hello"


def test_normalize_message_truncates_using_current_limit() -> None:
    _normalize_message_cached.cache_clear()

    assert normalize_message("0123456789abcdef", max_length=10) == "0123456789..."


def test_normalize_message_cache_respects_limit_argument() -> None:
    _normalize_message_cached.cache_clear()

    first = normalize_message("0123456789abcdef", max_length=10)

    second = normalize_message("0123456789abcdef", max_length=5)

    cache_info = _normalize_message_cached.cache_info()

    assert first == "0123456789..."
    assert second == "01234..."
    assert cache_info.misses == 2


def test_normalize_message_repeated_calls_use_cache() -> None:
    _normalize_message_cached.cache_clear()

    normalize_message("hello", max_length=10)
    normalize_message("hello", max_length=10)
    cache_info = _normalize_message_cached.cache_info()

    assert cache_info.hits == 1
    assert cache_info.misses == 1


def test_normalize_message_rejects_blank_text() -> None:
    _normalize_message_cached.cache_clear()

    with pytest.raises(ValueError, match="message must not be empty"):
        normalize_message("   ", max_length=10)


def test_normalize_message_rejects_non_positive_max_length() -> None:
    with pytest.raises(ValueError, match="max_length must be greater than 0"):
        normalize_message("hello", max_length=0)
