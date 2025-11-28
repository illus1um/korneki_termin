"""
Главный файл для запуска Telegram-бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import settings
from handlers import routers


async def main():
    """Основная функция для запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Запуск бота...")
    
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

