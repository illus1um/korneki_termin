"""
Обработчики команд и сообщений бота
"""
from .start import router as start_router
from .language import router as language_router
from .categories import router as categories_router
from .terms import router as terms_router
from .admin import router as admin_router

# Список всех роутеров (порядок важен!)
routers = [
    start_router,       # /start, /menu, home, back
    language_router,    # Выбор языка
    categories_router,  # Выбор категорий и подкатегорий
    terms_router,       # Просмотр результатов, пагинация, поиск
    admin_router,       # Админ-панель
]

__all__ = ['routers']

