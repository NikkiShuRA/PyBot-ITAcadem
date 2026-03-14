from aiogram import Router, F

from .user_profile import (
    user_profile_private_router,
    user_profile_group_router,
    user_profile_global_router,
)

from ...filters import create_chat_type_routers

profile_private_router, profile_group_router, profile_global_router = create_chat_type_routers("profile")

profile_private_router.include_router(user_profile_private_router)
profile_group_router.include_router(user_profile_group_router)
profile_global_router.include_router(user_profile_global_router)

profile_router = Router(name="profile")
profile_router.include_routers(
    profile_private_router,
    profile_group_router,
    profile_global_router,
)
