from aiogram.fsm.state import State, StatesGroup


# Состояния для Dialog в aiogram_dialog
class CreateProfileSG(StatesGroup):
    """States для диалога создания профиля."""

    first_name = State()
    last_name = State()
    patronymic = State()
    finish = State()
