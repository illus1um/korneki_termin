"""
Клавиатуры для категорий и подкатегорий
"""
from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import get_text, translate_category, translate_subcategory
from utils.category_mapper import get_mapper


def get_categories_keyboard(categories: List[str], lang: str = 'kk') -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с категориями (по 2 кнопки в ряд)
    
    Args:
        categories: Список названий категорий (на казахском из CSV)
        lang: Язык интерфейса ('kk' или 'ru')
        
    Returns:
        InlineKeyboardMarkup с кнопками категорий
    """
    keyboard = []
    mapper = get_mapper()
    
    # Группируем категории по 2 в ряд
    for i in range(0, len(categories), 2):
        row = []
        
        # Первая кнопка в ряду
        category1 = categories[i]
        cat_id1 = mapper.register_category(category1)
        # Переводим текст кнопки, но callback_data использует короткий ID
        display_text1 = translate_category(category1, lang) if lang == 'ru' else category1
        row.append(InlineKeyboardButton(
            text=display_text1,
            callback_data=f"cat:{cat_id1}"  # Короткий числовой ID
        ))
        
        # Вторая кнопка в ряду (если есть)
        if i + 1 < len(categories):
            category2 = categories[i + 1]
            cat_id2 = mapper.register_category(category2)
            display_text2 = translate_category(category2, lang) if lang == 'ru' else category2
            row.append(InlineKeyboardButton(
                text=display_text2,
                callback_data=f"cat:{cat_id2}"  # Короткий числовой ID
            ))
        
        keyboard.append(row)
    
    # Добавляем кнопку смены языка
    keyboard.append([
        InlineKeyboardButton(
            text=get_text('btn_change_lang', lang),
            callback_data="action:change_lang"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_subcategories_keyboard(subcategories: List[str], lang: str = 'kk') -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с подкатегориями (по 2 кнопки в ряд)
    
    Args:
        subcategories: Список названий подкатегорий (на казахском из CSV)
        lang: Язык интерфейса ('kk' или 'ru')
        
    Returns:
        InlineKeyboardMarkup с кнопками подкатегорий
    """
    keyboard = []
    mapper = get_mapper()
    
    # Группируем подкатегории по 2 в ряд
    for i in range(0, len(subcategories), 2):
        row = []
        
        # Первая кнопка в ряду
        subcat1 = subcategories[i]
        subcat_id1 = mapper.register_subcategory(subcat1)
        # Переводим текст кнопки, но callback_data использует короткий ID
        display_text1 = translate_subcategory(subcat1, lang) if lang == 'ru' else subcat1
        row.append(InlineKeyboardButton(
            text=display_text1,
            callback_data=f"sub:{subcat_id1}"  # Короткий числовой ID
        ))
        
        # Вторая кнопка в ряду (если есть)
        if i + 1 < len(subcategories):
            subcat2 = subcategories[i + 1]
            subcat_id2 = mapper.register_subcategory(subcat2)
            display_text2 = translate_subcategory(subcat2, lang) if lang == 'ru' else subcat2
            row.append(InlineKeyboardButton(
                text=display_text2,
                callback_data=f"sub:{subcat_id2}"  # Короткий числовой ID
            ))
        
        keyboard.append(row)
    
    # Добавляем навигационные кнопки
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

