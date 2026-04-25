"""Модуль бота IT Academ."""

from aiogram.fsm.state import State, StatesGroup


# Состояния для Dialog в aiogram_dialog
class CreateProfileSG(StatesGroup):
    """States для диалога регистрации пользователя."""

    welcome = State()
    contact = State()
    first_name = State()
    last_name = State()
    patronymic = State()
    competencies = State()
    finish = State()
