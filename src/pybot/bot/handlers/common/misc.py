from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from ....services.users import UserService
from ...filters import create_chat_type_routers

_, _, misc_global_router = create_chat_type_routers("start")


@misc_global_router.message(Command("ping"), flags={"rate_limit": "expensive"})
async def cmd_ping(
    message: Message,
    db: FromDishka[AsyncSession],
    user_service: FromDishka[UserService],
) -> None:
    if message.from_user is None:
        await message.answer("Hello, anonymous user!")
        return
    user = await user_service.get_or_create_user(
        db,
        message.from_user.id,
        message.from_user.first_name or "User",
    )

    is_admin = await user_service.is_admin(db, user.id)

    await message.answer(f"Hello, {user.first_name}! Admin: {is_admin}")
    await message.answer("pong")
