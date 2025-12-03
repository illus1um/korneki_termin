"""
Настройка структурированного логирования
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(
    name: str = 'bot',
    log_dir: Path = Path('logs'),
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Настройка логгера с ротацией файлов
    
    Args:
        name: Имя логгера
        log_dir: Директория для логов
        log_level: Уровень логирования
        max_bytes: Максимальный размер файла перед ротацией
        backup_count: Количество резервных файлов
        
    Returns:
        Настроенный логгер
    """
    # Создаём директорию для логов
    log_dir.mkdir(exist_ok=True)
    
    # Создаём логгер
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Удаляем существующие обработчики
    logger.handlers.clear()
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для файла (с ротацией)
    log_file = log_dir / f'{name}.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Обработчик для ошибок (отдельный файл)
    error_log_file = log_dir / f'{name}_errors.log'
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str = 'bot') -> logging.Logger:
    """
    Получить логгер (создаёт если не существует)
    
    Args:
        name: Имя логгера
        
    Returns:
        Логгер
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger

