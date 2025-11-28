"""
Утилиты для бота
"""
from .formatter import format_term, format_results_page
from .texts import get_text, TEXTS, translate_category, translate_subcategory

__all__ = [
    'format_term',
    'format_results_page',
    'get_text',
    'TEXTS',
    'translate_category',
    'translate_subcategory',
]

