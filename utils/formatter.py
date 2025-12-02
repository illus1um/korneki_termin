"""
Форматирование результатов поиска терминов
"""
from typing import Dict, List


def format_term(term_data: Dict[str, str], show_lang: bool = True, show_category: bool = True) -> str:
    """
    Форматирует данные термина в Markdown строку
    
    Args:
        term_data: Словарь с данными термина (term, description, category, subcategory, lang)
        show_lang: Показывать ли язык в метаданных
        show_category: Показывать ли категорию/подкатегорию в метаданных
        
    Returns:
        Отформатированная строка в формате Markdown
    """
    # Получаем данные и очищаем от лишних пробелов
    term = term_data.get('term', '').strip()
    description = term_data.get('description', '').strip()
    category = term_data.get('category', '').strip()
    subcategory = term_data.get('subcategory', '').strip()
    lang = term_data.get('lang', '').strip()
    
    # Если термин пустой, возвращаем пустую строку
    if not term:
        return ""
    
    # Формируем метаданные (только если они заполнены)
    meta_parts = []
    if show_category and category:
        meta_parts.append(category)
    if show_category and subcategory:
        meta_parts.append(subcategory)
    if show_lang and lang:
        meta_parts.append(lang)
    
    # Формируем строку результата
    # Экранируем специальные символы Markdown в названии термина
    term_escaped = _escape_markdown(term)
    result = f"**{term_escaped}**"
    
    if meta_parts:
        meta_str = " / ".join(meta_parts)
        result += f" _({meta_str})_"
    
    if description:
        result += f"\n{description}"
    
    return result


def _escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы Markdown
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст с экранированными символами
    """
    # Экранируем только те символы, которые могут сломать форматирование заголовка
    special_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    result = text
    for char in special_chars:
        result = result.replace(char, f'\\{char}')
    return result


def format_results_page(
    terms: List[Dict[str, str]],
    page: int = 1,
    per_page: int = 10,
    show_lang: bool = False,
    show_category: bool = False
) -> str:
    """
    Форматирует список терминов для отображения с пагинацией
    
    Args:
        terms: Список терминов для отображения
        page: Номер текущей страницы (начинается с 1)
        per_page: Количество элементов на странице
        show_lang: Показывать ли язык в метаданных
        show_category: Показывать ли категорию/подкатегорию для каждого термина
        
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
        formatted_term = format_term(term_data, show_lang=show_lang, show_category=show_category)
        result_parts.append(f"{i}. {formatted_term}")
    
    return "\n\n".join(result_parts)

