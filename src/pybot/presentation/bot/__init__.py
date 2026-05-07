"""Public Telegram presentation API.

External imports should stop at ``pybot.presentation.bot`` rather than
depending on the internal aiogram package layout.
"""

from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from . import tg_bot_run as tg_bot_run
    from .dialogs.user_reg import getters as registration_getters_module
    from .dialogs.user_reg import handlers as registration_handlers_module
    from .dialogs.user_reg import states as registration_states_module
    from .dialogs.user_reg.getters import get_registration_competencies
    from .dialogs.user_reg.handlers import (
        _handle_contact_input,
        _on_competence_skip_impl,
        _on_competence_submit_impl,
        _on_patronymic_input_impl,
        _on_patronymic_skip_impl,
        on_competence_selection_changed,
        on_first_name_input,
        on_last_name_input,
        request_contact_prompt,
    )
    from .dialogs.user_reg.states import CreateProfileSG
    from .handlers.broadcast.broadcast_commands import _extract_message_for_broadcast, broadcast_command
    from .handlers.common import start as start_handlers_module
    from .handlers.common.misc import cmd_chat_id
    from .handlers.common.start import cmd_start_private
    from .handlers.points import grand_points as grand_points_handlers
    from .handlers.points.leaderboard import handle_leaderboard
    from .handlers.profile import user_profile as profile_handlers_module
    from .handlers.profile.user_profile import cmd_profile_private
    from .handlers.roles import change_competences as change_competences_handlers
    from .handlers.roles import change_roles as change_roles_handlers
    from .handlers.roles.role_catalog import handle_show_all_roles
    from .handlers.roles.role_request_flow import accept_role_request, cmd_role_request, reject_role_request
    from .handlers.roles.show_roles import handle_show_roles
    from .keyboards.auth import request_contact_kb
    from .keyboards.role_request_keyboard import RoleRequestCB, get_admin_decision_kb
    from .middlewares import logger as logger_middleware_module
    from .middlewares.logger import LoggerMiddleware
    from .middlewares.rate_limit import RateLimitMiddleware
    from .middlewares.role import RoleMiddleware
    from .middlewares.user_activity import UserActivityMiddleware
    from .tg_bot_run import tg_bot_main

_MODULE_EXPORTS: Final[dict[str, str]] = {
    "change_competences_handlers": ".handlers.roles.change_competences",
    "change_roles_handlers": ".handlers.roles.change_roles",
    "grand_points_handlers": ".handlers.points.grand_points",
    "logger_middleware_module": ".middlewares.logger",
    "profile_handlers_module": ".handlers.profile.user_profile",
    "registration_getters_module": ".dialogs.user_reg.getters",
    "registration_handlers_module": ".dialogs.user_reg.handlers",
    "registration_states_module": ".dialogs.user_reg.states",
    "start_handlers_module": ".handlers.common.start",
    "tg_bot_run": ".tg_bot_run",
}

_ATTRIBUTE_EXPORTS: Final[dict[str, tuple[str, str]]] = {
    "CreateProfileSG": (".dialogs.user_reg.states", "CreateProfileSG"),
    "LoggerMiddleware": (".middlewares.logger", "LoggerMiddleware"),
    "RateLimitMiddleware": (".middlewares.rate_limit", "RateLimitMiddleware"),
    "RoleMiddleware": (".middlewares.role", "RoleMiddleware"),
    "RoleRequestCB": (".keyboards.role_request_keyboard", "RoleRequestCB"),
    "UserActivityMiddleware": (".middlewares.user_activity", "UserActivityMiddleware"),
    "_extract_message_for_broadcast": (".handlers.broadcast.broadcast_commands", "_extract_message_for_broadcast"),
    "_handle_contact_input": (".dialogs.user_reg.handlers", "_handle_contact_input"),
    "_on_competence_skip_impl": (".dialogs.user_reg.handlers", "_on_competence_skip_impl"),
    "_on_competence_submit_impl": (".dialogs.user_reg.handlers", "_on_competence_submit_impl"),
    "_on_patronymic_input_impl": (".dialogs.user_reg.handlers", "_on_patronymic_input_impl"),
    "_on_patronymic_skip_impl": (".dialogs.user_reg.handlers", "_on_patronymic_skip_impl"),
    "accept_role_request": (".handlers.roles.role_request_flow", "accept_role_request"),
    "broadcast_command": (".handlers.broadcast.broadcast_commands", "broadcast_command"),
    "cmd_chat_id": (".handlers.common.misc", "cmd_chat_id"),
    "cmd_profile_private": (".handlers.profile.user_profile", "cmd_profile_private"),
    "cmd_role_request": (".handlers.roles.role_request_flow", "cmd_role_request"),
    "cmd_start_private": (".handlers.common.start", "cmd_start_private"),
    "get_admin_decision_kb": (".keyboards.role_request_keyboard", "get_admin_decision_kb"),
    "get_registration_competencies": (".dialogs.user_reg.getters", "get_registration_competencies"),
    "handle_leaderboard": (".handlers.points.leaderboard", "handle_leaderboard"),
    "handle_show_all_roles": (".handlers.roles.role_catalog", "handle_show_all_roles"),
    "handle_show_roles": (".handlers.roles.show_roles", "handle_show_roles"),
    "on_competence_selection_changed": (".dialogs.user_reg.handlers", "on_competence_selection_changed"),
    "on_first_name_input": (".dialogs.user_reg.handlers", "on_first_name_input"),
    "on_last_name_input": (".dialogs.user_reg.handlers", "on_last_name_input"),
    "reject_role_request": (".handlers.roles.role_request_flow", "reject_role_request"),
    "request_contact_kb": (".keyboards.auth", "request_contact_kb"),
    "request_contact_prompt": (".dialogs.user_reg.handlers", "request_contact_prompt"),
    "tg_bot_main": (".tg_bot_run", "tg_bot_main"),
}

__all__ = list(_MODULE_EXPORTS) + list(_ATTRIBUTE_EXPORTS)


def _load_module(module_path: str) -> ModuleType:
    return import_module(module_path, __name__)


def __getattr__(name: str) -> object:
    if name in _MODULE_EXPORTS:
        module = _load_module(_MODULE_EXPORTS[name])
        globals()[name] = module
        return module

    if name in _ATTRIBUTE_EXPORTS:
        module_path, attribute_name = _ATTRIBUTE_EXPORTS[name]
        value = getattr(_load_module(module_path), attribute_name)
        globals()[name] = value
        return value

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
