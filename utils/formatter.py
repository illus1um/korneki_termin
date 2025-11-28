"""
Форматирование результатов поиска терминов
"""
from typing import Dict


def format_term(term_data: Dict[str, str]) -> str:
    """
    Форматирует данные термина в Markdown строку
    
    Args:
        term_data: Словарь с данными термина (term, description, category, subcategory, lang)
        
    Returns:
        Отформатированная строка в формате Markdown
    """
    term = term_data.get('term', '')
    description = term_data.get('description', '')
    category = term_data.get('category', '')
    subcategory = term_data.get('subcategory', '')
    lang = term_data.get('lang', '')
    
    # Формируем метаданные (только если они заполнены)
    meta_parts = []
    if category:
        meta_parts.append(category)
    if subcategory:
        meta_parts.append(subcategory)
    if lang:
        meta_parts.append(lang)
    
    # Формируем строку результата
    result = f"**{term}**"
    
    if meta_parts:
        meta_str = " / ".join(meta_parts)
        result += f" _({meta_str})_"
    
    result += f"\n{description}"
    
    return result

