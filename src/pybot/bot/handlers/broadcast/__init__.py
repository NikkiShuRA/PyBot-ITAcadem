from aiogram import Router, F

from ...filters import create_chat_type_routers

from .broadcast_commands import broadcast_command_private_router

broadcast_private_router, broadcast_group_router, broadcast_global_router = create_chat_type_routers("broadcast")

broadcast_private_router.include_router(broadcast_command_private_router)

broadcast_router = Router(name="broadcast")
broadcast_router.include_routers(
    broadcast_private_router,
    broadcast_group_router,
    broadcast_global_router,
)
