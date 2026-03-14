import pytest

from pybot.core.config import settings
from pybot.utils.normalize_message import _normalize_message_cached, normalize_message


def test_normalize_message_trims_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "broadcast_max_text_length", 10)
    _normalize_message_cached.cache_clear()

    assert normalize_message("  hello  ") == "hello"


def test_normalize_message_truncates_using_current_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "broadcast_max_text_length", 10)
    _normalize_message_cached.cache_clear()

    assert normalize_message("0123456789abcdef") == "0123456789..."


def test_normalize_message_cache_respects_limit_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    _normalize_message_cached.cache_clear()

    monkeypatch.setattr(settings, "broadcast_max_text_length", 10)
    first = normalize_message("0123456789abcdef")

    monkeypatch.setattr(settings, "broadcast_max_text_length", 5)
    second = normalize_message("0123456789abcdef")

    cache_info = _normalize_message_cached.cache_info()

    assert first == "0123456789..."
    assert second == "01234..."
    assert cache_info.misses == 2


def test_normalize_message_repeated_calls_use_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "broadcast_max_text_length", 10)
    _normalize_message_cached.cache_clear()

    normalize_message("hello")
    normalize_message("hello")
    cache_info = _normalize_message_cached.cache_info()

    assert cache_info.hits == 1
    assert cache_info.misses == 1


def test_normalize_message_rejects_blank_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "broadcast_max_text_length", 10)
    _normalize_message_cached.cache_clear()

    with pytest.raises(ValueError, match="message must not be empty"):
        normalize_message("   ")
