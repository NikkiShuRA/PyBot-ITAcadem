import textwrap

from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from ...filters import create_chat_type_routers

start_private_router, start_group_router, start_global_router = create_chat_type_routers("start")


# /start - в личном чате
@start_private_router.message(CommandStart())
async def cmd_start_private(message: Message, dialog_manager: DialogManager, db: AsyncSession) -> None:
    from ..profile.grand_profile import cmd_profile_private  # noqa: PLC0415

    await cmd_profile_private(message, dialog_manager, db)


# /start - в групповом чате
@start_global_router.message(CommandStart())
async def cmd_start_group(message: Message) -> None:
    await message.answer("Всем привет!")


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

# /help - в личномчате
@start_private_router.message(Command("help"))
async def cmd_help_private(message: Message) -> None:
    await message.answer(
        textwrap.dedent(
            """
            /start — запустить бота
            /help — список команд
            /info — информация о боте
            /profile — просмотр профиля
            /reputation_points - работа с системой репутации
            /academic_points - работа с академической системой
            """
        )
    )

# /help - в групповом чате
@start_group_router.message(Command("help"))
async def cmd_help_group(message: Message) -> None:
    await message.answer(
        textwrap.dedent(
            """
            /start — запустить бота
            /help — список команд
            /info — информация о боте
            /reputation_points - работа с системой репутации
            /academic_points - работа с академической системой
            """
        )
    )
