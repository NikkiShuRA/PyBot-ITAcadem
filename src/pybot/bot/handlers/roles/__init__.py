from aiogram import Router

from ...filters import create_chat_type_routers
from .change_competences import change_competence_global_router
from .change_roles import change_role_global_router
from .role_request_flow import role_request_private_router

roles_private_router, roles_group_router, roles_global_router = create_chat_type_routers("roles")

roles_global_router.include_router(change_role_global_router)
roles_global_router.include_router(change_competence_global_router)

roles_private_router.include_router(role_request_private_router)

roles_router = Router(name="roles")
roles_router.include_routers(
    roles_private_router,
    roles_group_router,
    roles_global_router,
)
