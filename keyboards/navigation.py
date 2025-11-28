"""
Навигационные клавиатуры
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import get_text


def get_navigation_keyboard(lang: str = 'kk', show_search: bool = False) -> InlineKeyboardMarkup:
    """
    Базовая навигационная клавиатура (Назад, Главная)
    
    Args:
        lang: Язык интерфейса
        show_search: Показывать ли кнопку поиска
        
    Returns:
        InlineKeyboardMarkup с навигационными кнопками
    """
    keyboard = []
    
    # Кнопка поиска (опционально)
    if show_search:
        keyboard.append([
            InlineKeyboardButton(
                text=get_text('btn_search', lang),
                callback_data="action:search"
            )
        ])
    
    # Кнопки Назад и Главная
    keyboard.append([
        InlineKeyboardButton(
            text=get_text('btn_back', lang),
            callback_data="action:back"
        ),
        InlineKeyboardButton(
            text=get_text('btn_home', lang),
            callback_data="action:home"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_results_keyboard(
    lang: str = 'kk',
    has_prev: bool = False,
    has_next: bool = False,
    show_search: bool = True
) -> InlineKeyboardMarkup:
    """
    Клавиатура для просмотра результатов с пагинацией
    
    Args:
        lang: Язык интерфейса
        has_prev: Есть ли предыдущая страница
        has_next: Есть ли следующая страница
        show_search: Показывать ли кнопку поиска
        
    Returns:
        InlineKeyboardMarkup с кнопками для результатов
    """
    keyboard = []
    
    # Кнопка поиска
    if show_search:
        keyboard.append([
            InlineKeyboardButton(
                text=get_text('btn_search', lang),
                callback_data="action:search"
            )
        ])
    
    # Пагинация (если есть несколько страниц)
    if has_prev or has_next:
        pagination_row = []
        
        if has_prev:
            pagination_row.append(InlineKeyboardButton(
                text=get_text('btn_prev', lang),
                callback_data="action:prev_page"
            ))
        
        if has_next:
            pagination_row.append(InlineKeyboardButton(
                text=get_text('btn_next', lang),
                callback_data="action:next_page"
            ))
        
        keyboard.append(pagination_row)
    
    # Навигационные кнопки
    keyboard.append([
        InlineKeyboardButton(
            text=get_text('btn_back', lang),
            callback_data="action:back"
        ),
        InlineKeyboardButton(
            text=get_text('btn_home', lang),
            callback_data="action:home"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_search_keyboard(lang: str = 'kk') -> InlineKeyboardMarkup:
    """
    Клавиатура для режима поиска
    
    Args:
        lang: Язык интерфейса
        
    Returns:
        InlineKeyboardMarkup с кнопками отмены и назад
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text('btn_cancel', lang),
                callback_data="action:cancel_search"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text('btn_back', lang),
                callback_data="action:back"
            )
        ]
    ])
    
    return keyboard

