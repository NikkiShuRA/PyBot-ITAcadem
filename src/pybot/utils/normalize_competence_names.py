from collections.abc import Sequence


def normalize_competence_names(competence_names: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(name.strip().lower() for name in competence_names if name.strip()))
