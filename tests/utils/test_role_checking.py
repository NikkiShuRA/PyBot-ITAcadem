from pybot.utils import has_any_role
import pytest


class TestHasAnyRoleValidCases:
    """✅ Тесты: valid role checks."""

    def test_user_has_required_role_single(self) -> None:
        """Пользователь имеет одну требуемую роль из одной."""

        user_roles = {"admin", "user"}
        required = "admin"

        assert has_any_role(user_roles, required) is True

    def test_user_has_required_role_from_multiple(self) -> None:
        """Пользователь имеет одну из нескольких требуемых ролей."""

        user_roles = {"user", "moderator"}
        required_roles = {"admin", "moderator"}

        assert has_any_role(user_roles, required_roles) is True

    def test_user_has_multiple_matching_roles(self) -> None:
        """Пользователь имеет несколько требуемых ролей."""

        user_roles = {"admin", "moderator", "user"}
        required_roles = {"admin", "moderator"}

        assert has_any_role(user_roles, required_roles) is True

    def test_user_has_all_roles(self) -> None:
        """Пользователь имеет все требуемые роли."""

        user_roles = {"admin", "moderator", "user"}
        required_roles = {"admin", "moderator", "user"}

        assert has_any_role(user_roles, required_roles) is True

    def test_empty_required_roles_always_true(self) -> None:
        """Пустой список требуемых ролей - всегда True."""

        user_roles = {"user"}
        required_roles = set()

        assert has_any_role(user_roles, required_roles) is True

    def test_empty_user_roles_with_empty_required_true(self) -> None:
        """Пользователь без ролей, требуемые пусты - True."""

        user_roles = set()
        required_roles = set()

        assert has_any_role(user_roles, required_roles) is True

    def test_string_required_roles_autoconverted(self) -> None:
        """Одна требуемая роль как строка - автоматически в set."""

        user_roles = {"admin", "user"}
        required = "admin"

        assert has_any_role(user_roles, required) is True

    @pytest.mark.parametrize(
        "user_roles,required",
        [
            ({"admin"}, {"admin"}),
            ({"admin", "user"}, {"admin"}),
            ({"admin", "user", "moderator"}, {"user"}),
            ({"admin", "user", "moderator"}, {"admin", "user"}),
        ],
    )
    def test_various_valid_combinations(self, user_roles: set[str], required: set[str]) -> None:
        """Батарея валидных комбинаций ролей."""

        assert has_any_role(user_roles, required) is True


class TestHasAnyRoleInvalidCases:
    """❌ Тесты: role checks that should return False."""

    def test_user_missing_required_role(self) -> None:
        """Пользователь НЕ имеет требуемую роль."""

        user_roles = {"user"}
        required = "admin"

        assert has_any_role(user_roles, required) is False

    def test_user_missing_all_required_roles(self) -> None:
        """Пользователь не имеет НИ ОДНОЙ из требуемых ролей."""

        user_roles = {"user", "guest"}
        required_roles = {"admin", "moderator"}

        assert has_any_role(user_roles, required_roles) is False

    def test_empty_user_roles_with_required(self) -> None:
        """У пользователя нет ролей, а требуются - False."""

        user_roles = set()
        required_roles = {"admin"}

        assert has_any_role(user_roles, required_roles) is False

    def test_case_sensitive_role_matching(self) -> None:
        """Проверка ролей чувствительна к регистру."""

        user_roles = {"Admin"}  # Заглавная буква
        required = "admin"  # Строчная

        # Функция не преобразует, поэтому это False
        assert has_any_role(user_roles, required) is False

    @pytest.mark.parametrize(
        "user_roles,required",
        [
            ({"user"}, {"admin"}),
            ({"guest"}, {"admin", "moderator"}),
            ({"viewer"}, {"editor", "admin"}),
            (set(), {"admin"}),
        ],
    )
    def test_various_invalid_combinations(self, user_roles: set[str], required: set[str]) -> None:
        """Батарея невалидных комбинаций ролей."""

        assert has_any_role(user_roles, required) is False


class TestHasAnyRoleEdgeCases:
    """🎯 Тесты: граничные случаи."""

    def test_single_character_role(self) -> None:
        """Роли из одного символа."""

        user_roles = {"a", "b"}
        required = {"a"}

        assert has_any_role(user_roles, required) is True

    def test_very_long_role_names(self) -> None:
        """Очень длинные названия ролей."""

        long_role = "can_delete_users_and_view_all_admin_panels_in_the_system"
        user_roles = {long_role, "user"}
        required = {long_role}

        assert has_any_role(user_roles, required) is True

    def test_roles_with_special_characters(self) -> None:
        """Роли со специальными символами."""

        user_roles = {"admin-v2", "user_manager", "api.read"}
        required = {"admin-v2"}

        assert has_any_role(user_roles, required) is True

    def test_roles_with_numbers(self) -> None:
        """Роли с числами."""

        user_roles = {"level1_user", "level2_moderator", "level3_admin"}
        required = {"level2_moderator"}

        assert has_any_role(user_roles, required) is True

    def test_unicode_roles(self) -> None:
        """Роли на других языках."""

        user_roles = {"администратор", "пользователь"}
        required = {"администратор"}

        assert has_any_role(user_roles, required) is True

    def test_many_user_roles(self) -> None:
        """Пользователь имеет много ролей."""

        user_roles = {f"role_{i}" for i in range(100)}
        required = {"role_50"}

        assert has_any_role(user_roles, required) is True

    def test_many_required_roles(self) -> None:
        """Много требуемых ролей."""

        user_roles = {"admin"}
        required_roles = {f"role_{i}" for i in range(100)}
        required_roles.add("admin")

        assert has_any_role(user_roles, required_roles) is True

    def test_string_required_roles_with_special_chars(self) -> None:
        """Строковая требуемая роль со специальными символами."""

        user_roles = {"admin-v2"}
        required = "admin-v2"

        assert has_any_role(user_roles, required) is True


class TestHasAnyRoleTypeHandling:
    """🔄 Тесты: обработка типов данных."""

    def test_required_roles_string_conversion(self) -> None:
        """Строка автоматически преобразуется в set."""

        user_roles = {"admin"}
        required_one_role = "admin"

        result = has_any_role(user_roles, required_one_role)
        assert result is True

    def test_required_roles_set_remains_set(self) -> None:
        """Set остаётся set."""

        user_roles = {"admin"}
        required_roles = {"admin"}

        result = has_any_role(user_roles, required_roles)
        assert result is True

    def test_string_matches_set_element(self) -> None:
        """Строковая требуемая роль ищется в set пользователя."""

        user_roles = {"moderator", "user"}
        required = "moderator"

        assert has_any_role(user_roles, required) is True

    def test_empty_string_role(self) -> None:
        """Пустая строка как требуемая роль."""

        user_roles = {"", "admin"}
        required = ""

        assert has_any_role(user_roles, required) is True

    def test_empty_string_in_required_set(self) -> None:
        """Пустая строка в наборе требуемых ролей."""

        user_roles = {"admin", ""}
        required_roles = {"", "moderator"}

        assert has_any_role(user_roles, required_roles) is True


class TestHasAnyRoleIntegration:
    """🔗 Интеграционные тесты."""

    def test_typical_admin_check(self) -> None:
        """Типичный сценарий: проверка прав администратора."""

        current_user_roles = {"user", "verified"}
        admin_roles = {"admin", "superadmin"}

        can_access_admin_panel = has_any_role(current_user_roles, admin_roles)
        assert can_access_admin_panel is False

    def test_typical_admin_check_success(self) -> None:
        """Типичный сценарий: пользователь имеет доступ администратора."""

        current_user_roles = {"admin", "user"}
        admin_roles = {"admin", "superadmin"}

        can_access_admin_panel = has_any_role(current_user_roles, admin_roles)
        assert can_access_admin_panel is True

    def test_permission_hierarchy_check(self) -> None:
        """Проверка иерархии прав: любой из высоких уровней подходит."""

        user_roles = {"user", "moderator"}
        elevated_roles = {"moderator", "admin", "superadmin"}

        has_elevated_access = has_any_role(user_roles, elevated_roles)
        assert has_elevated_access is True

    def test_feature_flag_based_on_roles(self) -> None:
        """Включение функции на основе ролей."""

        user_roles = {"beta_tester", "user"}
        beta_feature_roles = {"beta_tester", "admin"}

        can_use_beta_feature = has_any_role(user_roles, beta_feature_roles)
        assert can_use_beta_feature is True

    def test_multiple_permission_checks(self) -> None:
        """Несколько проверок прав в одной функции."""

        user_roles = {"user", "content_creator"}

        can_view = has_any_role(user_roles, "user")  # True
        can_create_content = has_any_role(user_roles, {"content_creator"})  # True
        can_delete_users = has_any_role(user_roles, {"admin"})  # False

        assert can_view is True
        assert can_create_content is True
        assert can_delete_users is False
