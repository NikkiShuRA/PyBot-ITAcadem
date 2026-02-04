"""
Доменные исключения для слоя Domain (DDD).
Все исключения наследуют от базового DomainError.
"""

from typing import Any


class DomainError(Exception):
    """Базовое исключение для всех доменных ошибок."""

    def __init__(self, message: str, code: str | None = None, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


# ============ ПОЛЬЗОВАТЕЛЬСКИЕ ОШИБКИ ============


class UserNotFoundError(DomainError):
    """Пользователь не найден в системе."""

    def __init__(self, user_id: int | None = None, telegram_id: int | None = None, phone: str | None = None) -> None:
        details = {}
        if user_id:
            details["user_id"] = user_id
        if telegram_id:
            details["telegram_id"] = telegram_id
        if phone:
            details["phone"] = phone

        msg = "Пользователь не найден"
        if user_id:
            msg += f" (ID: {user_id})"
        elif telegram_id:
            msg += f" (Telegram: {telegram_id})"
        elif phone:
            msg += f" (Phone: {phone})"

        super().__init__(msg, details=details)


class UsersNotFoundError(DomainError):
    """Пользователи не найдены в системе."""

    def __init__(self) -> None:
        super().__init__("Пользователи не найдены в системе")


class UserAlreadyExistsError(DomainError):
    """Пользователь уже существует."""

    def __init__(self, telegram_id: int | None = None, phone: str | None = None) -> None:
        details = {}
        if telegram_id:
            details["telegram_id"] = telegram_id
        if phone:
            details["phone"] = phone

        msg = "Пользователь уже существует в системе"
        super().__init__(msg, details=details)


class InvalidPointsValueError(DomainError):
    """Некорректное значение баллов."""

    def __init__(self, value: int, min_val: int = 0, max_val: int | None = None) -> None:
        details = {"value": value, "min": min_val}
        if max_val:
            details["max"] = max_val

        msg = f"Некорректное значение баллов: {value}. Минимум: {min_val}"
        if max_val:
            msg += f", Максимум: {max_val}"

        super().__init__(msg, details=details)


class ZeroPointsAdjustmentError(DomainError):
    """Попытка начислить/снять 0 баллов."""

    def __init__(self) -> None:
        super().__init__("Нельзя изменить баллы на 0")


class IncompatiblePointsTypeError(DomainError):
    """Несовместимые типы баллов при операции."""

    def __init__(self, type1: str, type2: str) -> None:
        super().__init__(f"Несовместимые типы баллов: {type1} и {type2}", details={"type1": type1, "type2": type2})


class LevelNotFoundError(DomainError):
    """Уровень не найден."""

    def __init__(self, level_id: int | None = None, points_type: str | None = None) -> None:
        details = {}
        if level_id:
            details["level_id"] = level_id
        if points_type:
            details["points_type"] = points_type

        msg = "Уровень не найден"
        super().__init__(msg, details=details)


class InvalidLevelTransitionError(DomainError):
    """Некорректный переход уровня."""

    def __init__(self, current_level_id: int, target_level_id: int, reason: str) -> None:
        super().__init__(
            f"Невозможен переход со уровня {current_level_id} на {target_level_id}: {reason}",
            details={"current": current_level_id, "target": target_level_id, "reason": reason},
        )


class RoleNotFoundError(DomainError):
    """Роль не найдена в системе."""

    def __init__(self, role_name: str) -> None:
        super().__init__(f"Роль '{role_name}' не найдена в системе", details={"role": role_name})


class RoleAlreadyAssignedError(DomainError):
    """Роль уже назначена пользователю."""

    def __init__(self, user_id: int, role_name: str) -> None:
        super().__init__(
            f"Пользователь {user_id} уже имеет роль '{role_name}'", details={"user_id": user_id, "role": role_name}
        )


class InvalidRoleChangeError(DomainError):
    """Ошибка при изменении роли."""

    def __init__(self, user_id: int, role_name: str, reason: str) -> None:
        super().__init__(
            f"Невозможно изменить роль пользователя {user_id} на '{role_name}': {reason}",
            details={"user_id": user_id, "role": role_name, "reason": reason},
        )


class UsersRolesNotFoundError(DomainError):
    """Роли пользователей не найдены в системе."""

    def __init__(self) -> None:
        super().__init__("Роли пользователей не найдены в системе")


class InvalidPhoneNumberError(DomainError):
    """Некорректный формат номера телефона."""

    def __init__(self, phone: str, reason: str = "") -> None:
        msg = f"Некорректный номер телефона: {phone}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg, details={"phone": phone})


class InitialLevelsNotFoundError(DomainError):
    """Начальные уровни не настроены в системе."""

    def __init__(self) -> None:
        super().__init__("В системе не настроены начальные уровни. Пожалуйста, свяжитесь с администратором.")


class DatabaseOperationError(DomainError):
    """Ошибка при работе с БД."""

    def __init__(self, operation: str, entity: str, reason: str | None = None) -> None:
        msg = f"Ошибка при {operation} {entity}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg, details={"operation": operation, "entity": entity})


class ValidationError(DomainError):
    """Ошибка валидации данных."""

    def __init__(self, field: str, value: Any, reason: str) -> None:
        super().__init__(f"Ошибка валидации поля '{field}': {reason}", details={"field": field, "value": value})


class PointsValidationError(DomainError):
    """Ошибка валидации баллов."""

    def __init__(self, field: str, value: Any, reason: str) -> None:
        super().__init__(f"Ошибка валидации баллов '{field}': {reason}", details={"field": field, "value": value})
