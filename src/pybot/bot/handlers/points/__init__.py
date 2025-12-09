from aiogram import Router, F

from .grand_points import grand_points_global_router as grand_points_global_router

from ...filters import create_chat_type_routers

points_private_router, points_group_router, points_global_router = create_chat_type_routers("points")

points_global_router.include_router(grand_points_global_router)

points_router = Router(name="points")
points_router.include_routers(
    points_private_router,
    points_group_router,
    points_global_router,
)
