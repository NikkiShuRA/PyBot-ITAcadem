from __future__ import annotations

import re
from collections.abc import Sequence

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from ....core import logger
from ....domain.exceptions import UserNotFoundError
from ....dto import UserReadDTO
from ....services.users import UserService
from ...filters import check_text_message_correction, create_chat_type_routers

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


async def _get_target_user_id_from_reply(message: Message) -> int | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    return None


async def _get_target_user_id_from_mention(message: Message, user_service: UserService) -> int | None:
    if not message.entities:
        return None

    for entity in message.entities:
        if entity.type == "text_mention" and entity.user is not None:
            target_tg_id = entity.user.id
            mentioned_user = await user_service.get_user_by_telegram_id(target_tg_id)
            if mentioned_user is not None:
                return mentioned_user.telegram_id
    return None


async def _get_target_user_id_from_text(message: Message, user_service: UserService) -> int | None:
    payload = _extract_payload_after_command(message)
    if payload is None or not payload:
        return None

    first_token = payload.split(maxsplit=1)[0]
    if not first_token.isdigit():
        return None

    target_tg_id = int(first_token)
    user = await user_service.get_user_by_telegram_id(target_tg_id)
    if user is None:
        return None
    return user.telegram_id


async def _resolve_target_user_telegram_id(
    message: Message, user_service: UserService
) -> tuple[int | None, str | None]:
    reply_target = await _get_target_user_id_from_reply(message)
    if reply_target is not None:
        return reply_target, "reply"

    mention_target = await _get_target_user_id_from_mention(message, user_service)
    if mention_target is not None:
        return mention_target, "mention"

    text_target = await _get_target_user_id_from_text(message, user_service)
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
    required: bool,
    fallback_user_id: int | None = None,
) -> tuple[UserReadDTO | None, str | None]:
    target_tg_id, target_source = await _resolve_target_user_telegram_id(message, user_service)
    if target_tg_id is not None:
        target_user = await user_service.get_user_by_telegram_id(target_tg_id)
        return target_user, target_source

    if fallback_user_id is not None:
        target_user = await user_service.get_user(fallback_user_id)
        return target_user, None

    if required:
        return None, target_source

    return None, target_source


@change_competence_global_router.message(
    Command("addcompetence"),
    flags={"role": "Admin", "rate_limit": "expensive"},
)
async def handle_add_competence(
    message: Message,
    user_service: FromDishka[UserService],
) -> None:
    target_user, target_source = await _resolve_target_user_for_command(message, user_service, required=True)
    if target_user is None:
        await message.reply(
            "Укажите пользователя через reply, text_mention или числовой telegram id.\n"
            "Формат: /addcompetence <tg_id|@mention> Python,SQL"
        )
        return

    competence_names = _extract_competence_names(message, target_source)
    if competence_names is None:
        await message.reply("Укажите список компетенций через запятую. Пример: /addcompetence 12345 Python,SQL")
        return

    try:
        await user_service.add_user_competencies_by_names(target_user.id, competence_names)
    except UserNotFoundError:
        await message.reply("Пользователь не найден.")
    except ValueError as error:
        await message.reply(f"Ошибка: {error}")
    except Exception:
        logger.exception("Unexpected error in handle_add_competence")
        await message.reply("Неожиданная ошибка при добавлении компетенций.")
    else:
        await message.reply(
            f"Компетенции добавлены пользователю {target_user.first_name}: {', '.join(competence_names)}"
        )


@change_competence_global_router.message(
    Command("removecompetence"),
    flags={"role": "Admin", "rate_limit": "expensive"},
)
async def handle_remove_competence(
    message: Message,
    user_service: FromDishka[UserService],
) -> None:
    target_user, target_source = await _resolve_target_user_for_command(message, user_service, required=True)
    if target_user is None:
        await message.reply(
            "Укажите пользователя через reply, text_mention или числовой telegram id.\n"
            "Формат: /removecompetence <tg_id|@mention> Python,SQL"
        )
        return

    competence_names = _extract_competence_names(message, target_source)
    if competence_names is None:
        await message.reply("Укажите список компетенций через запятую. Пример: /removecompetence 12345 Python,SQL")
        return

    try:
        await user_service.remove_user_competencies_by_names(target_user.id, competence_names)
    except UserNotFoundError:
        await message.reply("Пользователь не найден.")
    except ValueError as error:
        await message.reply(f"Ошибка: {error}")
    except Exception:
        logger.exception("Unexpected error in handle_remove_competence")
        await message.reply("Неожиданная ошибка при удалении компетенций.")
    else:
        await message.reply(
            f"Компетенции удалены у пользователя {target_user.first_name}: {', '.join(competence_names)}"
        )


@change_competence_global_router.message(Command("showcompetences"), flags={"role": "Admin"})
async def handle_show_competences(
    message: Message,
    user_service: FromDishka[UserService],
    user_id: int,
) -> None:
    fallback_user_id = user_id
    target_user, _ = await _resolve_target_user_for_command(
        message,
        user_service,
        required=False,
        fallback_user_id=fallback_user_id,
    )
    if target_user is None:
        await message.reply("Пользователь не найден.")
        return

    try:
        competencies = await user_service.get_user_competencies(target_user.id)
    except UserNotFoundError:
        await message.reply("Пользователь не найден.")
        return
    except Exception:
        logger.exception("Unexpected error in handle_show_competences")
        await message.reply("Неожиданная ошибка при получении компетенций.")
        return

    if not competencies:
        await message.reply(f"У пользователя {target_user.first_name} пока нет компетенций.")
        return

    competence_lines = "\n".join(f"- {competence.name}" for competence in competencies)
    await message.reply(f"Компетенции пользователя {target_user.first_name}:\n{competence_lines}")
