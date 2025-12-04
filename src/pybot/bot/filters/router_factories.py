from aiogram import Router

from .chat_filters import IS_ANY_CHAT, IS_GROUP, IS_PRIVATE


def create_chat_type_routers(name_prefix: str) -> tuple[Router, Router, Router]:
    """
    Создает тройку роутеров для разных типов чатов.

    Пример использования:
    private_router, group_router, global_router = create_chat_type_routers("start")
    """
    private_router = Router(name=f"{name_prefix}_private")
    private_router.message.filter(IS_PRIVATE)

    group_router = Router(name=f"{name_prefix}_group")
    group_router.message.filter(IS_GROUP)

    global_router = Router(name=f"{name_prefix}_global")
    global_router.message.filter(IS_ANY_CHAT)

    return private_router, group_router, global_router
