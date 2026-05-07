from functools import lru_cache
from html import escape


def telegram_user_link(
    user_id: int,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    fallback_label: str = "Пользователь",
) -> str:
    """Генерирует HTML-ссылку на профиль пользователя в Telegram.

    Args:
        user_id: Telegram ID пользователя.
        first_name: Имя пользователя.
        last_name: Фамилия пользователя.
        fallback_label: Текст ссылки, если имя и фамилия отсутствуют.

    Raises:
        ValueError: Если user_id <= 0.

    Returns:
        str: HTML-строка со ссылкой формата <a href='tg://user?id=...'>...</a>.
    """
    if user_id <= 0:
        raise ValueError("user_id must be greater than 0")

    normalized_first_name = first_name.strip() if first_name is not None else ""
    normalized_last_name = last_name.strip() if last_name is not None else ""
    normalized_fallback_label = fallback_label.strip() or "Пользователь"

    return _telegram_user_link_cached(
        user_id=user_id,
        first_name=normalized_first_name,
        last_name=normalized_last_name,
        fallback_label=normalized_fallback_label,
    )


@lru_cache(maxsize=512)
def _telegram_user_link_cached(
    *,
    user_id: int,
    first_name: str,
    last_name: str,
    fallback_label: str,
) -> str:
    name_parts = [part for part in (first_name, last_name) if part]
    link_label = " ".join(name_parts) if name_parts else fallback_label
    safe_label = escape(link_label, quote=False)

    return f"<a href='tg://user?id={user_id}'>{safe_label}</a>"
