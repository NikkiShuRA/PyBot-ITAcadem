from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from ....domain.exceptions import UserNotFoundError
from ....services.users import UserService
from ...filters import create_chat_type_routers
from ...texts import PING_ANONYMOUS, ping_status

_, _, misc_global_router = create_chat_type_routers("start")


@misc_global_router.message(Command("ping"), flags={"rate_limit": "expensive", "role": {"Student", "Mentor", "Admin"}})
async def cmd_ping(
    message: Message,
    user_service: FromDishka[UserService],
    user_id: int,
) -> None:
    if message.from_user is None:
        await message.answer(PING_ANONYMOUS)
        return

    try:
        user = await user_service.get_user(user_id)
    except UserNotFoundError:
        await message.answer(PING_ANONYMOUS)
        return

    is_admin = await user_service.check_user_role(user.id, "Admin")
    await message.answer(ping_status(user.first_name, is_admin))
