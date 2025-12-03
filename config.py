"""
Конфигурация бота
Загружает настройки из .env файла с использованием pydantic-settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    BOT_TOKEN: str
    ADMIN_IDS: str = ""  # ID админов через запятую: "123456789,987654321"
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
    @property
    def admin_ids_list(self) -> list[int]:
        """Получить список ID админов"""
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip().isdigit()]


# Создаем экземпляр настроек
settings = Settings()

