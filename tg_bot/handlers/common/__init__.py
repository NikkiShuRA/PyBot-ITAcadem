from aiogram import Router, F

from . import start, misc

# Роутер для личных чатов
private_router = Router()
private_router.message.filter(F.chat.type == "private")

# Роутер для групп/супергрупп
group_router = Router()
group_router.message.filter(F.chat.type.in_({"group", "supergroup"}))

# Роутер для всех типов чатов
global_router = Router()
global_router.message.filter(F.chat.type.in_({"private", "group", "supergroup"}))


# Подключаем хендлеры
private_router.include_router(start.private_router)
private_router.include_router(misc.private_router)

group_router.include_router(start.group_router)
group_router.include_router(misc.group_router)

global_router.include_router(start.global_router)
global_router.include_router(misc.global_router)
