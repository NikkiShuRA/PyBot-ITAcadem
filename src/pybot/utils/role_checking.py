def has_any_role(user_roles: set[str], required_roles: set[str] | str) -> bool:
    """Проверяет наличие хотя бы одной из требуемых ролей у пользователя.

    Args:
        user_roles: Множество ролей пользователя.
        required_roles: Роль (строка) или множество ролей, необходимых для доступа.

    Returns:
        bool: True, если у пользователя есть хотя бы одна из требуемых ролей, иначе False.
    """
    if isinstance(required_roles, str):
        required_roles = {required_roles}
    if not required_roles:
        return True
    return bool(user_roles & required_roles)
