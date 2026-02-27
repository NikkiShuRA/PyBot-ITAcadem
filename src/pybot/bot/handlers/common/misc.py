from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from ....services.users import UserService
from ...filters import create_chat_type_routers

_, _, misc_global_router = create_chat_type_routers("start")


@misc_global_router.message(Command("ping"), flags={"rate_limit": "expensive", "role": {"Student", "Mentor", "Admin"}})
async def cmd_ping(
    message: Message,
    user_service: FromDishka[UserService],
    user_id: int,
) -> None:
    if message.from_user is None:
        await message.answer("Hello, anonymous user!")
        return

    user = await user_service.get_user(user_id)

    if user is None:
        await message.answer("Hello, anonymous user!")
        return

    is_admin = await user_service.check_user_role(user.id, "Admin")

    await message.answer(f"Hello, {user.first_name}! Admin: {is_admin}")
    await message.answer("pong")
