# tg_bot/handlers/user/__init__.py
from aiogram import Router, F

# from . import profile_create
from .create_profile_dialog import profile_create_dialog

# Диалоги
user_dialogs = profile_create_dialog

# Роутер для личных чатов
private_router = Router()
private_router.message.filter(F.chat.type == "private")

# Роутер для групп/супергрупп
group_router = Router()
group_router.message.filter(F.chat.type.in_({"group", "supergroup"}))

# Роутер для всех типов чатов
global_router = Router()
global_router.message.filter(F.chat.type.in_({"private", "group", "supergroup"}))

# Общий роутер модуля
user_router = Router()
user_router.include_routers(user_dialogs, private_router, group_router, global_router)