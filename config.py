"""
Конфигурация бота
Загружает настройки из .env файла с использованием pydantic-settings
"""
import re
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    BOT_TOKEN: str
    ADMIN_IDS: str = ""  # ID админов через запятую: "123456789,987654321"
    
    # Rate limiting
    RATE_LIMIT_DEFAULT: int = 50  # Лимит для обычных пользователей (было 20)
    RATE_LIMIT_PERIOD: int = 120  # Период в секундах (было 60, теперь 2 минуты)
    RATE_LIMIT_ADMIN: int = 200  # Лимит для админов (было 100)
    RATE_LIMIT_ADMIN_PERIOD: int = 120  # Период для админов (было 60)
    
    # Валидация
    MAX_QUERY_LENGTH: int = 200  # Максимальная длина поискового запроса
    
    # Аналитика
    ANALYTICS_BATCH_SIZE: int = 10  # Размер батча для записи аналитики
    ANALYTICS_BATCH_TIMEOUT: float = 1.0  # Таймаут батча в секундах
    ANALYTICS_QUEUE_MAXSIZE: int = 1000  # Максимальный размер очереди аналитики
    
    # Результаты
    RESULTS_PER_PAGE: int = 10  # Количество результатов на странице
    MAX_SEARCH_RESULTS: int = 50  # Максимальное количество результатов поиска
    
    # Rate limit memory
    RATE_LIMIT_MAX_USERS: int = 10000  # Максимальное количество пользователей в памяти
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
    @field_validator('BOT_TOKEN')
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Валидация формата BOT_TOKEN"""
        if not v:
            raise ValueError("BOT_TOKEN не может быть пустым")
        # Telegram bot token формат: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
        pattern = r'^\d+:[A-Za-z0-9_-]{35}$'
        if not re.match(pattern, v):
            raise ValueError(
                "BOT_TOKEN имеет неверный формат. "
                "Ожидается формат: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            )
        return v
    
    @property
    def admin_ids_list(self) -> list[int]:
        """Получить список ID админов"""
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip().isdigit()]


# Создаем экземпляр настроек
settings = Settings()

