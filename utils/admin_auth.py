"""
Утилиты для проверки прав администратора
"""
from config import settings


def is_admin(user_id: int) -> bool:
    """
    Проверка, является ли пользователь администратором
    
    Args:
        user_id: Telegram ID пользователя
        
    Returns:
        True если пользователь админ, False иначе
    """
    return user_id in settings.admin_ids_list


def require_admin(func):
    """
    Декоратор для проверки прав администратора перед выполнением функции
    
    Использование:
        @require_admin
        async def admin_command(message: Message):
            ...
    """
    from functools import wraps
    from aiogram.types import Message, CallbackQuery
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Ищем user_id в аргументах
        user_id = None
        for arg in args:
            if isinstance(arg, (Message, CallbackQuery)):
                user_id = arg.from_user.id
                break
        
        if user_id is None or not is_admin(user_id):
            # Пытаемся отправить сообщение об ошибке
            for arg in args:
                if isinstance(arg, Message):
                    await arg.answer("❌ У вас нет прав администратора")
                    return
                elif isinstance(arg, CallbackQuery):
                    await arg.answer("❌ У вас нет прав администратора", show_alert=True)
                    return
            return
        
        return await func(*args, **kwargs)
    
    return wrapper

