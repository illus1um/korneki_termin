"""
Клавиатура выбора языка
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import get_text


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора языка интерфейса
    
    Returns:
        InlineKeyboardMarkup с кнопками выбора языка
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🇰🇿 Қазақша",
                callback_data="lang:kk"
            ),
            InlineKeyboardButton(
                text="🇷🇺 Русский",
                callback_data="lang:ru"
            )
        ]
    ])
    
    return keyboard

