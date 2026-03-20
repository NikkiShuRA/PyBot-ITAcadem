from __future__ import annotations

import re
from collections.abc import Sequence

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from ....core import logger
from ....domain.exceptions import CommandTargetNotSpecifiedError, UserNotFoundError
from ....dto import UserReadDTO
from ....services import CompetenceService
from ....services.user_services import UserCompetenceService, UserService
from ...filters import check_text_message_correction, create_chat_type_routers
from ...texts import (
    COMPETENCE_UNEXPECTED_ERROR,
    TARGET_NOT_FOUND,
    competence_add_success,
    competence_catalog,
    competence_list,
    competence_list_required,
    competence_none,
    competence_remove_success,
    competence_target_required,
    competence_validation_error,
)

(_, _, change_competence_global_router) = create_chat_type_routers("grand_points")


def _mask_text_mentions(message: Message, text: str) -> str:
    if not message.entities:
        return text

    chars = list(text)
    text_len = len(chars)
    for entity in message.entities:
        if entity.type != "text_mention":
            continue
        start = max(entity.offset, 0)
        end = min(entity.offset + entity.length, text_len)
        for index in range(start, end):
            chars[index] = " "
    return "".join(chars)


def _extract_payload_after_command(message: Message) -> str | None:
    text = check_text_message_correction(message)
    if text is None:
        return None

    masked_text = _mask_text_mentions(message, text)
    parts = masked_text.split(maxsplit=1)
    if len(parts) == 1:
        return ""
    return parts[1].strip()


def _extract_target_token_from_payload(payload: str) -> str | None:
    target_token_match = re.match(r"^(@\S+|\d+)\b", payload)
    if target_token_match is None:
        return None
    return target_token_match.group(1)


def _extract_numeric_target_token(message: Message) -> int | None:
    payload = _extract_payload_after_command(message)
    if payload is None or payload == "":
        return None

    target_token = _extract_target_token_from_payload(payload)
    if target_token is None or not target_token.isdigit():
        return None

    return int(target_token)


def _has_explicit_target_token(message: Message) -> bool:
    payload = _extract_payload_after_command(message)
    if payload is None or payload == "":
        return False
    return _extract_target_token_from_payload(payload) is not None


async def _get_target_user_id_from_reply(message: Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    return None


async def _get_target_user_id_from_mention(message: Message) -> int | None:
    if not message.entities:
        return None

    for entity in message.entities:
        if entity.type == "text_mention" and entity.user is not None:
            return entity.user.id
    return None


async def _get_target_user_id_from_text(message: Message) -> int | None:
    payload = _extract_payload_after_command(message)
    if payload is None or payload == "":
        return None

    target_token = _extract_target_token_from_payload(payload)
    if target_token is None or not target_token.isdigit():
        return None

    return int(target_token)


async def _resolve_target_user_telegram_id(message: Message) -> tuple[int | None, str | None]:
    reply_target = await _get_target_user_id_from_reply(message)
    if reply_target is not None:
        return reply_target, "reply"

    mention_target = await _get_target_user_id_from_mention(message)
    if mention_target is not None:
        return mention_target, "mention"

    text_target = await _get_target_user_id_from_text(message)
    if text_target is not None:
        return text_target, "text"

    return None, None


def _normalize_competence_names(raw_names: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw_name in raw_names:
        clean_name = raw_name.strip()
        if not clean_name:
            continue
        lowered = clean_name.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(clean_name)
    return normalized


def _extract_competence_names(message: Message, target_source: str | None) -> list[str] | None:
    payload = _extract_payload_after_command(message)
    if payload is None:
        return None

    if target_source != "reply":
        target_token_match = re.match(r"^(@\S+|\d+)\s+(.*)$", payload)
        if target_token_match:
            payload = target_token_match.group(2).strip()

    names = _normalize_competence_names(payload.split(","))
    if not names:
        return None
    return names


async def _resolve_target_user_for_command(
    message: Message,
    user_service: UserService,
    *,
    command_name: str,
    required: bool,
    fallback_user_id: int | None = None,
) -> tuple[UserReadDTO, str | None]:
    target_tg_id, target_source = await _resolve_target_user_telegram_id(message)
    if target_tg_id is not None:
        target_user = await user_service.find_user_by_telegram_id(target_tg_id)
        if target_user is None:
            raise UserNotFoundError(telegram_id=target_tg_id)
        return target_user, target_source

    if _has_explicit_target_token(message):
        numeric_target = _extract_numeric_target_token(message)
        if numeric_target is not None:
            raise UserNotFoundError(telegram_id=numeric_target)
        raise UserNotFoundError()

    if fallback_user_id is not None:
        try:
            target_user = await user_service.get_user(fallback_user_id)
        except UserNotFoundError as err:
            raise UserNotFoundError(user_id=fallback_user_id) from err
        return target_user, None

    if required:
        raise CommandTargetNotSpecifiedError(command_name=command_name)

    raise UserNotFoundError()


@change_competence_global_router.message(
    Command("addcompetence"),
    flags={"role": "Admin", "rate_limit": "expensive"},
)
async def handle_add_competence(
    message: Message,
    user_service: FromDishka[UserService],
    user_competence_service: FromDishka[UserCompetenceService],
) -> None:
    try:
        target_user, target_source = await _resolve_target_user_for_command(
            message,
            user_service,
            command_name="addcompetence",
            required=True,
        )
    except CommandTargetNotSpecifiedError:
        await message.reply(competence_target_required("addcompetence"))
        return
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
        return

    competence_names = _extract_competence_names(message, target_source)
    if competence_names is None:
        await message.reply(competence_list_required("addcompetence"))
        return

    try:
        await user_competence_service.add_user_competencies_by_names(target_user.id, competence_names)
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
    except ValueError as error:
        await message.reply(competence_validation_error(str(error)))
    except Exception:
        logger.exception("Unexpected error in handle_add_competence")
        await message.reply(COMPETENCE_UNEXPECTED_ERROR)
    else:
        await message.reply(competence_add_success(target_user.first_name, competence_names))


@change_competence_global_router.message(
    Command("removecompetence"),
    flags={"role": "Admin", "rate_limit": "expensive"},
)
async def handle_remove_competence(
    message: Message,
    user_service: FromDishka[UserService],
    user_competence_service: FromDishka[UserCompetenceService],
) -> None:
    try:
        target_user, target_source = await _resolve_target_user_for_command(
            message,
            user_service,
            command_name="removecompetence",
            required=True,
        )
    except CommandTargetNotSpecifiedError:
        await message.reply(competence_target_required("removecompetence"))
        return
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
        return

    competence_names = _extract_competence_names(message, target_source)
    if competence_names is None:
        await message.reply(competence_list_required("removecompetence"))
        return

    try:
        await user_competence_service.remove_user_competencies_by_names(target_user.id, competence_names)
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
    except ValueError as error:
        await message.reply(competence_validation_error(str(error)))
    except Exception:
        logger.exception("Unexpected error in handle_remove_competence")
        await message.reply(COMPETENCE_UNEXPECTED_ERROR)
    else:
        await message.reply(competence_remove_success(target_user.first_name, competence_names))


@change_competence_global_router.message(
    Command("showcompetences"),
    flags={"rate_limit": "moderate"},
)
async def handle_show_competences(
    message: Message,
    user_service: FromDishka[UserService],
    user_competence_service: FromDishka[UserCompetenceService],
    user_id: int,
) -> None:
    try:
        target_user, _ = await _resolve_target_user_for_command(
            message,
            user_service,
            command_name="showcompetences",
            required=False,
            fallback_user_id=user_id,
        )
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
        return

    try:
        competencies = await user_competence_service.find_user_competencies(target_user.id)
    except UserNotFoundError:
        await message.reply(TARGET_NOT_FOUND)
        return
    except Exception:
        logger.exception("Unexpected error in handle_show_competences")
        await message.reply(COMPETENCE_UNEXPECTED_ERROR)
        return

    if not competencies:
        await message.reply(competence_none(target_user.first_name))
        return

    await message.reply(competence_list(target_user.first_name, competencies))


@change_competence_global_router.message(
    Command("competences"),
    flags={"rate_limit": "moderate"},
)
async def handle_show_all_competences(
    message: Message,
    competence_service: FromDishka[CompetenceService],
) -> None:
    try:
        competencies = await competence_service.find_all_competencies()
    except Exception:
        logger.exception("Unexpected error in handle_show_all_competences")
        await message.reply(COMPETENCE_UNEXPECTED_ERROR)
        return

    await message.reply(
        competence_catalog(competencies),
        parse_mode="HTML",
    )
