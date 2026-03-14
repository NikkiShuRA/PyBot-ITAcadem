from collections.abc import Sequence
from functools import lru_cache


def normalize_competence_names(competence_names: Sequence[str]) -> list[str]:
    return list(_normalize_competence_names_cached(tuple(competence_names)))


@lru_cache(maxsize=256)
def _normalize_competence_names_cached(competence_names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(name.strip().lower() for name in competence_names if name.strip()))
