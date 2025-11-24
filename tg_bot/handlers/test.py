from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from services.users import check_profile 

router = Router()

my_filter = F.chat.type.in_({"private", "group", "supergroup"})
my_filter_private = F.chat.type.in_({"private"})

@router.message(CommandStart())
async def cmd_start(message: Message, db: AsyncSession):
    await message.reply(f"Ушёл на обед, ждите позже 🫠")

@router.message(Command(f"clear"), my_filter)
async def cmd_start(message: Message, db: AsyncSession):
    await message.reply(f"Не хочу чистить тут 😫")

@router.message(Command(f"hello"), my_filter)
async def cmd_start(message: Message, db: AsyncSession):
    await message.reply(f"Привет {message.from_user.username} 👋 Сейчас проходит тест")

@router.message(Command(f"help"), my_filter)
async def cmd_start(message: Message, db: AsyncSession):
    await message.reply(f"Тебе уже ничем не помочь 🤡")


@router.message(Command(f"check"), my_filter_private)
async def cmd_start(message: Message, db: AsyncSession):
    answer = await check_profile(db)
    await message.answer(f"{answer}")