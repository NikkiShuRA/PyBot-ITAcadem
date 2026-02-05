from aiogram import Router, F

from .change_roles import change_role_global_router

from ...filters import create_chat_type_routers

roles_private_router, roles_group_router, roles_global_router = create_chat_type_routers("roles")

roles_global_router.include_router(change_role_global_router)

roles_router = Router(name="roles")
roles_router.include_routers(
    roles_private_router,
    roles_group_router,
    roles_global_router,
)
