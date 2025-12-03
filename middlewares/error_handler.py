"""
Middleware для глобальной обработки ошибок
"""
import traceback
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, ErrorEvent
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramConflictError,
    TelegramRetryAfter,
    TelegramServerError
)
from utils.logger import get_logger
from utils.admin_auth import is_admin
from config import settings

logger = get_logger('error_handler')


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Middleware для перехвата и обработки всех исключений
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с перехватом ошибок"""
        try:
            return await handler(event, data)
        except TelegramRetryAfter as e:
            # Telegram просит подождать
            logger.warning(f"Telegram rate limit: retry after {e.retry_after}s")
            # Не отправляем сообщение пользователю, просто логируем
            return
        except TelegramBadRequest as e:
            # Неправильный запрос (например, слишком длинное сообщение)
            logger.error(f"TelegramBadRequest: {e.message}")
            
            # Пытаемся отправить понятное сообщение пользователю
            await self._handle_bad_request(event, e)
            return
        except TelegramNetworkError as e:
            # Сетевая ошибка
            logger.error(f"TelegramNetworkError: {e}")
            # Не отправляем сообщение, чтобы не спамить при проблемах с сетью
            return
        except TelegramConflictError as e:
            # Конфликт (например, другой экземпляр бота запущен)
            logger.critical(f"TelegramConflictError: {e}")
            # Критическая ошибка - нужно остановить бота
            raise
        except TelegramServerError as e:
            # Ошибка сервера Telegram
            logger.error(f"TelegramServerError: {e}")
            return
        except Exception as e:
            # Любая другая ошибка
            logger.error(
                f"Unexpected error: {type(e).__name__}: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            
            # Уведомляем админов о критических ошибках
            await self._notify_admins(event, e)
            
            # Пытаемся отправить понятное сообщение пользователю
            await self._handle_generic_error(event, e)
            return
    
    async def _handle_bad_request(self, event: TelegramObject, error: TelegramBadRequest):
        """Обработка TelegramBadRequest"""
        # Пытаемся найти способ отправить сообщение
        try:
            if hasattr(event, 'answer') and callable(event.answer):
                await event.answer(
                    "⚠️ Сообщение слишком длинное или содержит недопустимые символы. "
                    "Попробуйте сократить запрос."
                )
            elif hasattr(event, 'message') and event.message:
                await event.message.answer(
                    "⚠️ Сообщение слишком длинное или содержит недопустимые символы. "
                    "Попробуйте сократить запрос."
                )
            elif hasattr(event, 'callback_query') and event.callback_query:
                await event.callback_query.answer(
                    "⚠️ Ошибка: сообщение слишком длинное",
                    show_alert=True
                )
        except Exception:
            # Если не удалось отправить, просто логируем
            pass
    
    async def _handle_generic_error(self, event: TelegramObject, error: Exception):
        """Обработка общей ошибки"""
        try:
            if hasattr(event, 'answer') and callable(event.answer):
                await event.answer(
                    "❌ Произошла ошибка. Пожалуйста, попробуйте позже или используйте /menu"
                )
            elif hasattr(event, 'message') and event.message:
                await event.message.answer(
                    "❌ Произошла ошибка. Пожалуйста, попробуйте позже или используйте /menu"
                )
            elif hasattr(event, 'callback_query') and event.callback_query:
                await event.callback_query.answer(
                    "❌ Произошла ошибка. Попробуйте позже.",
                    show_alert=True
                )
        except Exception:
            # Если не удалось отправить, просто логируем
            pass
    
    async def _notify_admins(self, event: TelegramObject, error: Exception):
        """Уведомление админов о критических ошибках"""
        # Получаем user_id из события
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif hasattr(event, 'callback_query') and event.callback_query:
            user_id = event.callback_query.from_user.id
        
        # Логируем информацию об ошибке
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'user_id': user_id,
            'traceback': traceback.format_exc()
        }
        
        logger.critical(f"Critical error occurred: {error_info}")
        
        # В будущем можно добавить отправку уведомлений админам через Telegram
        # Пока просто логируем

