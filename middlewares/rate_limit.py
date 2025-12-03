"""
Middleware для ограничения частоты запросов (Rate Limiting)
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from utils.logger import get_logger

logger = get_logger('rate_limit')


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов
    """
    
    def __init__(
        self,
        default_limit: int = 20,  # Запросов
        default_period: int = 60,  # Секунд
        admin_limit: int = 100,  # Для админов
        admin_period: int = 60
    ):
        """
        Args:
            default_limit: Лимит запросов для обычных пользователей
            default_period: Период в секундах
            admin_limit: Лимит для админов
            admin_period: Период для админов
        """
        self.default_limit = default_limit
        self.default_period = timedelta(seconds=default_period)
        self.admin_limit = admin_limit
        self.admin_period = timedelta(seconds=admin_period)
        
        # Хранилище: user_id -> [(timestamp, ...), ...]
        self._requests: Dict[int, list] = defaultdict(list)
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
        self._requests[user_id] = [
            ts for ts in self._requests[user_id] if ts > cutoff
        ]
    
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
        
        # Проверяем лимит
        current_requests = len(self._requests[user_id])
        
        if current_requests >= limit:
            # Вычисляем время до следующего разрешённого запроса
            if self._requests[user_id]:
                oldest_request = min(self._requests[user_id])
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
        
        # Регистрируем запрос
        self._requests[user_id].append(datetime.now())
        
        # Продолжаем обработку
        return await handler(event, data)

