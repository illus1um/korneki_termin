import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import settings
from handlers import routers
from services import TermsService, AnalyticsService
from middlewares import RateLimitMiddleware, ErrorHandlerMiddleware
from utils.category_mapper import get_mapper


async def main():
    """Основная функция для запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Запуск бота...")
    
    # Инициализация маппера категорий для обоих языков
    logger.info("Инициализация маппера категорий...")
    terms_service = TermsService()
    mapper = get_mapper()
    
    # Регистрируем категории и подкатегории для обоих языков
    for lang in ['kk', 'ru']:
        categories = terms_service.get_categories(lang)
        for cat in categories:
            mapper.register_category(cat)
            subcats = terms_service.get_subcategories(cat, lang)
            for subcat in subcats:
                mapper.register_subcategory(subcat)
    
    logger.info(f"Маппер инициализирован для обоих языков")
    
    # Инициализация аналитики и запуск фонового воркера
    analytics = AnalyticsService()
    await analytics.start()
    logger.info("Сервис аналитики запущен")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Подключение middleware (порядок важен!)
    rate_limit_middleware = RateLimitMiddleware(
        default_limit=20,  # 20 запросов
        default_period=60,  # за 60 секунд
        admin_limit=100,
        admin_period=60
    )
    # Устанавливаем ID админов если они есть
    admin_ids = settings.admin_ids_list
    if admin_ids:
        rate_limit_middleware.set_admin_ids(admin_ids)
        logger.info(f"Rate limit для админов: {admin_ids}")
    
    error_handler_middleware = ErrorHandlerMiddleware()
    
    # Регистрируем middleware (сначала error handler, потом rate limit)
    dp.message.middleware(error_handler_middleware)
    dp.callback_query.middleware(error_handler_middleware)
    dp.message.middleware(rate_limit_middleware)
    dp.callback_query.middleware(rate_limit_middleware)
    
    logger.info("Middleware подключены")
    
    # Подключение всех роутеров из handlers
    for router in routers:
        dp.include_router(router)
    
    logger.info("Все роутеры подключены")
    
    # Удаление вебхуков (если были) и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен и готов к работе!")
    
    try:
        # Оптимизированные настройки polling для лучшей производительности
        # aiogram 3.x автоматически обрабатывает обновления конкурентно
        # allowed_updates ограничивает типы обновлений для экономии трафика
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query"],  # Только нужные типы обновлений
            drop_pending_updates=True,
            # close_bot_session=False - оставляем управление сессией вручную
        )
    finally:
        # Останавливаем аналитику перед завершением
        await analytics.stop()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == '__main__':
    asyncio.run(main())

