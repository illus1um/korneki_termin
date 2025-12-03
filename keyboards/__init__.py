"""
Клавиатуры для бота
"""
from .language import get_language_keyboard
from .categories import get_categories_keyboard, get_subcategories_keyboard
from .navigation import get_navigation_keyboard, get_results_keyboard, get_search_keyboard
from .admin import (
    get_admin_main_keyboard,
    get_admin_stats_keyboard,
    get_admin_back_keyboard,
    get_admin_export_keyboard,
    get_admin_backup_keyboard
)

__all__ = [
    'get_language_keyboard',
    'get_categories_keyboard',
    'get_subcategories_keyboard',
    'get_navigation_keyboard',
    'get_results_keyboard',
    'get_search_keyboard',
    'get_admin_main_keyboard',
    'get_admin_stats_keyboard',
    'get_admin_back_keyboard',
    'get_admin_export_keyboard',
    'get_admin_backup_keyboard',
]

