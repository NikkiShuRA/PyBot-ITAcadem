from .grand_profile import show_profile

from aiogram import Router, F

from .grand_profile import (
    grand_profile_private_router,
    grand_profile_group_router,
    grand_profile_global_router,
)

from ...filters import create_chat_type_routers

profile_private_router, profile_group_router, profile_global_router = create_chat_type_routers("profile")

profile_private_router.include_router(grand_profile_private_router)
profile_group_router.include_router(grand_profile_group_router)
profile_global_router.include_router(grand_profile_global_router)

profile_router = Router(name="profile")
profile_router.include_routers(
    profile_private_router,
    profile_group_router,
    profile_global_router,
)

__all__ = [
    "show_profile",
]