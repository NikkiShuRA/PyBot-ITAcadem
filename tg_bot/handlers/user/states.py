from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager

# Состояния для Dialog в aiogram_dialog
class ProfileSG(StatesGroup):
    """States для диалога создания профиля."""
    first_name = State()
    last_name = State()
    patronymic = State()
    finish = State()
