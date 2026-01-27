# tg_bot/handlers/user/__init__.py
from aiogram import Router, F

# from . import profile_create
from .windows import profile_create_dialog

from ...filters import create_chat_type_routers

# Диалоги
user_dialogs = profile_create_dialog

user_private_router, user_group_router, user_global_router = create_chat_type_routers("user")

# Общий роутер модуля
user_router = Router()
user_router.include_routers(user_dialogs, user_private_router, user_group_router, user_global_router)
