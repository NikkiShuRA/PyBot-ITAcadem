from pybot.utils.normalize_competence_names import (
    _normalize_competence_names_cached,
    normalize_competence_names,
)


def test_normalize_competence_names_normalizes_and_deduplicates() -> None:
    _normalize_competence_names_cached.cache_clear()

    result = normalize_competence_names([" Python ", "python", "", "SQL"])

    assert result == ["python", "sql"]


def test_normalize_competence_names_returns_fresh_list_on_each_call() -> None:
    _normalize_competence_names_cached.cache_clear()

    first = normalize_competence_names(["Python", "SQL"])
    second = normalize_competence_names(["Python", "SQL"])

    first.append("docker")

    assert second == ["python", "sql"]


def test_normalize_competence_names_repeated_calls_use_cache() -> None:
    _normalize_competence_names_cached.cache_clear()

    normalize_competence_names(["Python", "SQL"])
    normalize_competence_names(["Python", "SQL"])
    cache_info = _normalize_competence_names_cached.cache_info()

    assert cache_info.hits == 1
    assert cache_info.misses == 1
