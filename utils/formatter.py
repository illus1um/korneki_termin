"""
Форматирование результатов поиска терминов
"""
from typing import Dict, List


def format_term(term_data: Dict[str, str], show_lang: bool = True) -> str:
    """
    Форматирует данные термина в Markdown строку
    
    Args:
        term_data: Словарь с данными термина (term, description, category, subcategory, lang)
        show_lang: Показывать ли язык в метаданных
        
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
    if show_lang and lang:
        meta_parts.append(lang)
    
    # Формируем строку результата
    result = f"**{term}**"
    
    if meta_parts:
        meta_str = " / ".join(meta_parts)
        result += f" _({meta_str})_"
    
    result += f"\n{description}"
    
    return result


def format_results_page(
    terms: List[Dict[str, str]],
    page: int = 1,
    per_page: int = 10,
    show_lang: bool = False
) -> str:
    """
    Форматирует список терминов для отображения с пагинацией
    
    Args:
        terms: Список терминов для отображения
        page: Номер текущей страницы (начинается с 1)
        per_page: Количество элементов на странице
        show_lang: Показывать ли язык в метаданных
        
    Returns:
        Отформатированная строка с терминами
    """
    if not terms:
        return ""
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_terms = terms[start_idx:end_idx]
    
    result_parts = []
    
    for i, term_data in enumerate(page_terms, start=start_idx + 1):
        formatted_term = format_term(term_data, show_lang=show_lang)
        result_parts.append(f"{i}. {formatted_term}")
    
    return "\n\n".join(result_parts)

