"""
Обработчики команд и сообщений бота
"""
from .start import router as start_router
from .terms import router as terms_router

# Список всех роутеров
routers = [start_router, terms_router]

__all__ = ['routers']

