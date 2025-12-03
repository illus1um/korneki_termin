"""
Клавиатуры для админ-панели
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import get_text


def get_admin_main_keyboard(lang: str = 'kk') -> InlineKeyboardMarkup:
    """Главное меню админки"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin:stats"
            ),
            InlineKeyboardButton(
                text="🔍 Топ запросы",
                callback_data="admin:top"
            )
        ],
        [
            InlineKeyboardButton(
                text="💚 Здоровье бота",
                callback_data="admin:health"
            ),
            InlineKeyboardButton(
                text="❌ Ошибки",
                callback_data="admin:errors"
            )
        ],
        [
            InlineKeyboardButton(
                text="📤 Экспорт",
                callback_data="admin:export"
            ),
            InlineKeyboardButton(
                text="💾 Бэкапы",
                callback_data="admin:backup"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚙️ Настройки",
                callback_data="admin:settings"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="action:home"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_stats_keyboard(lang: str = 'kk') -> InlineKeyboardMarkup:
    """Клавиатура для статистики"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📊 За 7 дней",
                callback_data="admin:stats:7"
            ),
            InlineKeyboardButton(
                text="📊 За 30 дней",
                callback_data="admin:stats:30"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="admin:main"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_back_keyboard(lang: str = 'kk') -> InlineKeyboardMarkup:
    """Кнопка назад в админке"""
    keyboard = [[
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin:main"
        )
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_export_keyboard(lang: str = 'kk') -> InlineKeyboardMarkup:
    """Клавиатура для экспорта"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📊 Экспорт аналитики",
                callback_data="admin:export:analytics"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Экспорт терминов",
                callback_data="admin:export:terms"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="admin:main"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_backup_keyboard(lang: str = 'kk') -> InlineKeyboardMarkup:
    """Клавиатура для бэкапов"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="💾 Создать бэкап",
                callback_data="admin:backup:create"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Список бэкапов",
                callback_data="admin:backup:list"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="admin:main"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

