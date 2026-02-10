def has_any_role(user_roles: set[str], required_roles: set[str] | str) -> bool:
    if isinstance(required_roles, str):
        required_roles = {required_roles}
    if not required_roles:
        return True
    return bool(user_roles & required_roles)
