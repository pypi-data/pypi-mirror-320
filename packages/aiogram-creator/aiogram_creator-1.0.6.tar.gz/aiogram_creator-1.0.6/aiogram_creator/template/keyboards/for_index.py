import aiogram.types as types
from aiogram.utils.keyboard import InlineKeyboardMarkup


def menu() -> InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="Hello", callback_data="hello")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
