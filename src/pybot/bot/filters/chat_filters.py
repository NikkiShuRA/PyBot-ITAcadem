from aiogram import F

IS_PRIVATE = F.chat.type == "private"
IS_GROUP = F.chat.type.in_({"group", "supergroup"})
IS_ANY_CHAT = F.chat.type.in_({"private", "group", "supergroup"})
