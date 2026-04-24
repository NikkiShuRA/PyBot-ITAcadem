"""Модуль бота IT Academ."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from ...presentation.texts import BUTTON_SEND_CONTACT

request_contact_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BUTTON_SEND_CONTACT, request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)
