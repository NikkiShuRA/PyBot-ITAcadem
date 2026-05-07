"""Модуль бота IT Academ."""

from aiogram_dialog import DialogManager

type CompetenceOption = tuple[int, str]
COMPETENCE_OPTION_SIZE = 2


async def get_registration_competencies(
    dialog_manager: DialogManager,
    **kwargs: object,
) -> dict[str, list[CompetenceOption]]:
    """Вспомогательная функция get_registration_competencies."""
    del kwargs
    raw_options = dialog_manager.dialog_data.get("registration_competencies")
    return {"registration_competencies": _normalize_competence_options(raw_options)}


def _normalize_competence_options(raw_options: object) -> list[CompetenceOption]:
    if not isinstance(raw_options, list):
        return []

    normalized_options: list[CompetenceOption] = []
    for option in raw_options:
        if not isinstance(option, tuple) or len(option) != COMPETENCE_OPTION_SIZE:
            continue

        competence_id, competence_name = option
        if isinstance(competence_id, int) and isinstance(competence_name, str):
            normalized_options.append((competence_id, competence_name))

    return normalized_options
