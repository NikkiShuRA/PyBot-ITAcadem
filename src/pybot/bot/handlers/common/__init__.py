from aiogram import Router, F

from .start import (
    start_private_router,
    start_group_router,
    start_global_router,
)

from .misc import misc_global_router

from ...filters import create_chat_type_routers

common_private_router, common_group_router, common_global_router = create_chat_type_routers("common")

common_private_router.include_router(start_private_router)
common_group_router.include_router(start_group_router)
common_global_router.include_router(start_global_router)
common_global_router.include_router(misc_global_router)

common_router = Router(name="common")
common_router.include_routers(
    common_private_router,
    common_group_router,
    common_global_router,
)
