import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher

from config import settings
from handlers import routers
from services import TermsService
from utils.category_mapper import get_mapper


async def health_check(request):
    """Простой health check endpoint для Render"""
    return web.Response(text="OK")


async def start_web_server():
    """Запуск простого HTTP сервера для Render"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    port = int(os.getenv('PORT', 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"HTTP сервер запущен на порту {port}")


async def main():
    """Основная функция для запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Запуск бота...")
    
    # Запускаем HTTP сервер в фоне (для Render)
    await start_web_server()
    
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
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Подключение всех роутеров из handlers
    for router in routers:
        dp.include_router(router)
    
    logger.info("Все роутеры подключены")
    
    # Удаление вебхуков (если были) и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен и готов к работе!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())

