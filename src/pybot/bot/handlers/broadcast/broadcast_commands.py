from collections.abc import Sequence

from aiogram.filters.command import Command
from aiogram.types import Message
from dishka import FromDishka

from ....core.config import settings
from ....core.constants import RoleEnum
from ....domain.exceptions import BroadcastMessageNotSpecifiedError
from ....dto import BroadcastDTO, CompetenceBroadcastDTO, CompetenceReadDTO, RoleBroadcastDTO
from ....services.broadcast import BroadcastService
from ....services.competence import CompetenceService
from ...filters import check_text_message_correction, create_chat_type_routers
from ...texts import BROADCAST_MESSAGE_REQUIRED, BROADCAST_USAGE, broadcast_unknown_target

(broadcast_command_private_router, _, _) = create_chat_type_routers("broadcast")
TARGET_AND_MESSAGE_PARTS = 2


def _extract_role(target_token: str) -> RoleEnum | None:
    for role in RoleEnum:
        if role.value.casefold() == target_token.casefold():
            return role
    return None


def _extract_all_ping(target_token: str) -> bool:
    return target_token.casefold() == "@all"


def _extract_competence(target_token: str, competencies: Sequence[CompetenceReadDTO]) -> CompetenceReadDTO | None:
    for competence in competencies:
        if competence.name.casefold() == target_token.casefold():
            return competence
    return None


def _extract_payload_after_command(message: Message) -> str | None:
    text = check_text_message_correction(message)
    if text is None:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) < TARGET_AND_MESSAGE_PARTS:
        return None
    return parts[1].strip()


def _extract_target_token(message: Message) -> str | None:
    payload = _extract_payload_after_command(message)
    if payload is None:
        return None
    target_parts = payload.split(maxsplit=1)
    if not target_parts:
        return None
    return target_parts[0].strip()


async def _extract_message_for_broadcast(message: Message, target_token: str) -> str:
    payload = _extract_payload_after_command(message)
    if payload is None or payload == "":
        raise BroadcastMessageNotSpecifiedError()

    target_and_message = payload.split(maxsplit=1)
    if len(target_and_message) < TARGET_AND_MESSAGE_PARTS:
        raise BroadcastMessageNotSpecifiedError()

    if target_and_message[0].casefold() != target_token.casefold():
        raise BroadcastMessageNotSpecifiedError()

    broadcast_message = target_and_message[1].strip()
    if not broadcast_message:
        raise BroadcastMessageNotSpecifiedError()

    return broadcast_message


@broadcast_command_private_router.message(
    Command("broadcast"),
    flags={"role": settings.broadcast_allowed_roles, "rate_limit": "expensive"},
)
async def broadcast_command(
    message: Message,
    broadcast_service: FromDishka[BroadcastService],
    competence_service: FromDishka[CompetenceService],
) -> None:
    target_token = _extract_target_token(message)
    if target_token is None:
        await message.reply(BROADCAST_USAGE)
        return

    try:
        broadcast_message = await _extract_message_for_broadcast(message, target_token)
    except BroadcastMessageNotSpecifiedError:
        await message.reply(BROADCAST_MESSAGE_REQUIRED)
        return

    if _extract_all_ping(target_token):
        await broadcast_service.broadcast_for_all(BroadcastDTO(broadcast_message=broadcast_message))
        return

    role = _extract_role(target_token)
    if role is not None:
        await broadcast_service.broadcast_for_users_with_role(
            RoleBroadcastDTO(broadcast_message=broadcast_message, role_name=role.value)
        )
        return

    competencies = await competence_service.get_all_competencies()
    competence = _extract_competence(target_token, competencies)
    if competence is not None:
        await broadcast_service.broadcast_for_users_with_competence(
            CompetenceBroadcastDTO(broadcast_message=broadcast_message, competence_id=competence.id)
        )
        return

    await message.reply(broadcast_unknown_target(competencies))
