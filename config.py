"""
Конфигурация бота
Загружает настройки из .env файла с использованием pydantic-settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    BOT_TOKEN: str
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


# Создаем экземпляр настроек
settings = Settings()

