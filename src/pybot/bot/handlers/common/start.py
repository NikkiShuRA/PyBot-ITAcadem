import textwrap

from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Contact, Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from ....services.users import attach_telegram_to_user, get_user_by_phone, get_user_by_telegram_id
from ...dialogs.user.states import CreateProfileSG
from ...filters import create_chat_type_routers
from ...keyboards.auth import request_contact_kb

start_private_router, start_group_router, start_global_router = create_chat_type_routers("start")


# /start - в личном чате
@start_private_router.message(CommandStart())
async def cmd_start_private(message: Message, db: AsyncSession) -> None:
    if message.from_user:
        user = await get_user_by_telegram_id(db, message.from_user.id)
    else:
        await message.answer(
            "Произошла ошибка при обработке пользователя.",
        )
        return
    if user:
        await message.answer("Ты уже авторизован, /help — список команд.")
        return
    else:
        await message.answer(
            "Для авторизации отправь свой номер телефона кнопкой ниже.",
            reply_markup=request_contact_kb,
        )


# /start - в групповом чате
@start_global_router.message(CommandStart())
async def cmd_start_group(message: Message) -> None:
    await message.answer("Всем привет!")


@start_private_router.message(F.contact)
async def handle_contact(message: Message, dialog_manager: DialogManager, db: AsyncSession) -> None:
    contact: Contact | None = message.contact
    if message.from_user:
        if contact and contact.user_id != message.from_user.id:
            await message.answer("Нужен именно твой номер, а не чужой.")
            return
    else:
        await message.answer(
            "Произошла ошибка при обработке пользователя.",
        )
        return
    if contact is None:
        await message.answer("Произошла ошибка при получении контакта. Попробуй ещё раз.")
        return

    phone: str = contact.phone_number
    tg_id: int = message.from_user.id

    user = await get_user_by_phone(db, phone)
    if user:
        await attach_telegram_to_user(db, user, tg_id)
        await message.answer(f"Найден существующий профиль. Твой ID: {user.id}")
        return

    # пользователя нет — запускаем диалог создания профиля
    await dialog_manager.start(
        CreateProfileSG.first_name,
        data={"phone": phone, "tg_id": tg_id},
    )


# /info - в личном/групповом чате
@start_global_router.message(Command("info"))
async def cmd_info(message: Message) -> None:
    await message.answer(
        textwrap.dedent(
            """
            Привет! 👋
            Я бот платформы информационного комьюнити ITAcadem на базе StartUP (СИЭУиП).

            ITAcadem — это современная образовательная платформа для студентов СИЭУиП и всех, кто хочет учиться программированию и развиваться в IT-сфере. 💻✨
            Платформа объединяет практическое обучение, проектную деятельность и профессиональный рост в единой интерактивной среде.

            Моя задача — сделать твоё развитие удобным, наглядным и доступным в удалённом формате. 🚀
            Через меня ты можешь проще взаимодействовать с платформой и IT‑сообществом.

            Что я могу предложить уже сейчас:
             • Просмотр твоего профиля и прогресса в обучении 📊
             • Отслеживание выполненных задач и текущих активностей ✅
             • Напоминания о важных дедлайнах и событиях ⏰
             • Уведомления о мероприятиях и активностях IT‑комьюнити 📅

            По мере развития платформы мои возможности будут расширяться, а взаимодействие с ITAcadem станет ещё удобнее и полезнее для тебя. 😉

            GitHub проекта — https://github.com/NikkiShuRA/PyBot-ITAcadem.git
            """  # noqa: E501
        )
    )


# /help - в личном чате
@start_group_router.message(Command("help"))
@start_private_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        textwrap.dedent(
            """
            /start — запустить бота
            /help — список команд
            /info — информация о боте
            """
        )
    )
