"""
Утилиты для валидации и санитизации пользовательского ввода
"""
import re
from typing import Optional
from pathlib import Path


# Константы валидации
MAX_USERNAME_LENGTH = 100
ALLOWED_LANGUAGES = {'kk', 'ru'}
MAX_CALLBACK_DATA_LENGTH = 64  # Telegram limit


def get_max_query_length() -> int:
    """Получить максимальную длину запроса из конфига"""
    try:
        from config import settings
        return getattr(settings, 'MAX_QUERY_LENGTH', 200)
    except:
        return 200


def sanitize_query(query: str) -> Optional[str]:
    """
    Санитизация поискового запроса
    
    Args:
        query: Исходный запрос
        
    Returns:
        Очищенный запрос или None если невалидный
    """
    if not query:
        return None
    
    # Удаляем лишние пробелы
    cleaned = ' '.join(query.split())
    
    # Проверяем длину
    max_length = get_max_query_length()
    if len(cleaned) > max_length:
        return None
    
    # Удаляем опасные символы (но оставляем кириллицу, латиницу, цифры, пробелы, дефисы)
    # Разрешаем: буквы, цифры, пробелы, дефисы, апострофы
    cleaned = re.sub(r'[^\w\s\-\'а-яёА-ЯЁқҚғҒңҢөӨұҰіІ]', '', cleaned, flags=re.UNICODE)
    
    # Проверяем, что осталось что-то после очистки
    if not cleaned.strip():
        return None
    
    return cleaned.strip()


def validate_language(lang: str) -> bool:
    """
    Валидация кода языка
    
    Args:
        lang: Код языка
        
    Returns:
        True если валидный, False иначе
    """
    return lang in ALLOWED_LANGUAGES


def validate_category_id(category_id: str) -> Optional[int]:
    """
    Валидация ID категории из callback_data
    
    Args:
        category_id: Строка с ID
        
    Returns:
        ID как int или None если невалидный
    """
    try:
        cat_id = int(category_id)
        # Проверяем разумный диапазон (1-10000)
        if 1 <= cat_id <= 10000:
            return cat_id
    except (ValueError, TypeError):
        pass
    return None


def validate_subcategory_id(subcategory_id: str) -> Optional[int]:
    """
    Валидация ID подкатегории из callback_data
    
    Args:
        subcategory_id: Строка с ID
        
    Returns:
        ID как int или None если невалидный
    """
    try:
        subcat_id = int(subcategory_id)
        # Проверяем разумный диапазон (1-10000)
        if 1 <= subcat_id <= 10000:
            return subcat_id
    except (ValueError, TypeError):
        pass
    return None


def validate_callback_data(callback_data: str) -> bool:
    """
    Валидация callback_data для предотвращения инъекций
    
    Args:
        callback_data: Данные callback
        
    Returns:
        True если валидный, False иначе
    """
    if not callback_data:
        return False
    
    # Проверяем длину (Telegram limit)
    if len(callback_data) > MAX_CALLBACK_DATA_LENGTH:
        return False
    
    # Разрешаем только безопасные символы: буквы, цифры, двоеточия, подчеркивания, дефисы
    if not re.match(r'^[a-zA-Z0-9:_\-]+$', callback_data):
        return False
    
    return True


def sanitize_path(file_path: str, base_dir: Path) -> Optional[Path]:
    """
    Санитизация пути к файлу для предотвращения path traversal
    
    Args:
        file_path: Исходный путь
        base_dir: Базовая директория
        
    Returns:
        Безопасный Path или None если невалидный
    """
    if not file_path:
        return None
    
    try:
        # Нормализуем путь
        path = Path(file_path)
        
        # Убираем относительные переходы
        path = path.resolve()
        base_dir = base_dir.resolve()
        
        # Проверяем, что путь внутри базовой директории
        try:
            path.relative_to(base_dir)
        except ValueError:
            # Путь вне базовой директории - небезопасно
            return None
        
        return path
    except (ValueError, OSError):
        return None


def validate_days(days: int, min_days: int = 1, max_days: int = 365) -> Optional[int]:
    """
    Валидация количества дней
    
    Args:
        days: Количество дней
        min_days: Минимум
        max_days: Максимум
        
    Returns:
        Валидное количество дней или None
    """
    try:
        days_int = int(days)
        if min_days <= days_int <= max_days:
            return days_int
    except (ValueError, TypeError):
        pass
    return None


def validate_limit(limit: int, min_limit: int = 1, max_limit: int = 1000) -> Optional[int]:
    """
    Валидация лимита
    
    Args:
        limit: Лимит
        min_limit: Минимум
        max_limit: Максимум
        
    Returns:
        Валидный лимит или None
    """
    try:
        limit_int = int(limit)
        if min_limit <= limit_int <= max_limit:
            return limit_int
    except (ValueError, TypeError):
        pass
    return None


def sanitize_username(username: Optional[str]) -> str:
    """
    Санитизация имени пользователя
    
    Args:
        username: Имя пользователя
        
    Returns:
        Очищенное имя или пустая строка
    """
    if not username:
        return ''
    
    # Ограничиваем длину
    if len(username) > MAX_USERNAME_LENGTH:
        username = username[:MAX_USERNAME_LENGTH]
    
    # Удаляем опасные символы
    username = re.sub(r'[^\w\s\-_.]', '', username)
    
    return username.strip()

