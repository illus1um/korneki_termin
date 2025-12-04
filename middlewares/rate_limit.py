"""
Middleware для ограничения частоты запросов (Rate Limiting)
"""
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Tuple
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from utils.logger import get_logger
from config import settings

logger = get_logger('rate_limit')


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов с ограничением памяти
    """
    
    def __init__(
        self,
        default_limit: int = None,  # Запросов
        default_period: int = None,  # Секунд
        admin_limit: int = None,  # Для админов
        admin_period: int = None,
        max_users: int = None  # Максимальное количество пользователей в памяти
    ):
        """
        Args:
            default_limit: Лимит запросов для обычных пользователей
            default_period: Период в секундах
            admin_limit: Лимит для админов
            admin_period: Период для админов
            max_users: Максимальное количество пользователей в памяти
        """
        # Используем значения из конфига если не указаны
        self.default_limit = default_limit or settings.RATE_LIMIT_DEFAULT
        self.default_period = timedelta(seconds=default_period or settings.RATE_LIMIT_PERIOD)
        self.admin_limit = admin_limit or settings.RATE_LIMIT_ADMIN
        self.admin_period = timedelta(seconds=admin_period or settings.RATE_LIMIT_ADMIN_PERIOD)
        self.max_users = max_users or settings.RATE_LIMIT_MAX_USERS
        
        # Хранилище: user_id -> [(timestamp, ...), ...]
        # Используем OrderedDict для LRU-подобного поведения
        self._requests: OrderedDict[int, list] = OrderedDict()
        self._admin_ids: set = set()
    
    def set_admin_ids(self, admin_ids: list[int]):
        """Установить список ID админов"""
        self._admin_ids = set(admin_ids)
    
    def _is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь админом"""
        return user_id in self._admin_ids
    
    def _clean_old_requests(self, user_id: int, period: timedelta):
        """Удалить старые запросы"""
        cutoff = datetime.now() - period
        if user_id in self._requests:
            self._requests[user_id] = [
                ts for ts in self._requests[user_id] if ts > cutoff
            ]
            # Если список пуст, удаляем пользователя
            if not self._requests[user_id]:
                self._requests.pop(user_id, None)
    
    def _enforce_memory_limit(self):
        """Ограничение памяти - удаляем старых пользователей если превышен лимит"""
        if len(self._requests) > self.max_users:
            # Удаляем самых старых пользователей (FIFO)
            users_to_remove = list(self._requests.keys())[:len(self._requests) - self.max_users]
            for user_id in users_to_remove:
                self._requests.pop(user_id, None)
            logger.warning(
                f"Rate limit memory limit reached ({self.max_users}). "
                f"Removed {len(users_to_remove)} old users."
            )
    
    def _check_rate_limit(self, user_id: int) -> Tuple[bool, int]:
        """
        Проверка rate limit
        
        Returns:
            (is_allowed, remaining_seconds)
        """
        is_admin = self._is_admin(user_id)
        limit = self.admin_limit if is_admin else self.default_limit
        period = self.admin_period if is_admin else self.default_period
        
        # Очищаем старые запросы
        self._clean_old_requests(user_id, period)
        
        # Проверяем лимит (пользователь может быть удален после очистки)
        current_requests = len(self._requests.get(user_id, []))
        
        if current_requests >= limit:
            # Вычисляем время до следующего разрешённого запроса
            user_requests = self._requests.get(user_id, [])
            if user_requests:
                oldest_request = min(user_requests)
                next_allowed = oldest_request + period
                remaining = (next_allowed - datetime.now()).total_seconds()
                return False, max(0, int(remaining))
            return False, int(period.total_seconds())
        
        return True, 0
    
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict
    ):
        """Обработка события"""
        # Получаем user_id из события
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif hasattr(event, 'callback_query') and event.callback_query:
            user_id = event.callback_query.from_user.id
        
        # Если не удалось определить user_id, пропускаем
        if user_id is None:
            return await handler(event, data)
        
        # Ограничиваем память
        self._enforce_memory_limit()
        
        # Проверяем rate limit
        is_allowed, remaining = self._check_rate_limit(user_id)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for user {user_id}. "
                f"Remaining: {remaining}s"
            )
            # Не обрабатываем событие, просто возвращаемся
            # (пользователь не получит ответ, что и является ограничением)
            return
        
        # Регистрируем запрос (перемещаем в конец для LRU)
        now = datetime.now()
        if user_id in self._requests:
            self._requests[user_id].append(now)
            # Перемещаем в конец OrderedDict для LRU
            self._requests.move_to_end(user_id)
        else:
            self._requests[user_id] = [now]
        
        # Продолжаем обработку
        return await handler(event, data)

