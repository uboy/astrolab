"""
Конфигурация логирования для бота
"""

import logging
import logging.handlers
import os
from pathlib import Path
from utils.config import settings


class LogLevel:
    """Уровни логирования"""
    OFF = "OFF"
    DEBUG = "DEBUG"
    ERROR_WARNING = "ERROR_WARNING"


def get_log_level() -> int:
    """
    Получить уровень логирования на основе настройки

    Returns:
        Уровень логирования для logging
    """
    level = getattr(settings, 'LOG_LEVEL', LogLevel.ERROR_WARNING).upper()

    if level == LogLevel.OFF:
        return logging.CRITICAL + 1  # Выключено
    elif level == LogLevel.DEBUG:
        return logging.DEBUG
    elif level == LogLevel.ERROR_WARNING:
        return logging.WARNING
    else:
        return logging.WARNING  # По умолчанию ошибки и предупреждения


def setup_logging():
    """
    Настроить логирование для всего приложения
    """
    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Получаем уровень логирования
    log_level = get_log_level()

    # Если логирование выключено, возвращаемся
    if log_level > logging.CRITICAL:
        return

    # Создаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Убираем существующие обработчики (если есть)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Консольный обработчик (для всех уровней)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый обработчик (только ошибки и выше)
    error_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)

    # Файловый обработчик для всех сообщений (если DEBUG)
    if log_level <= logging.DEBUG:
        debug_file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "debug.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=3
        )
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(formatter)
        logger.addHandler(debug_file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для модуля

    Args:
        name: Имя модуля/класса

    Returns:
        Logger instance
    """
    return logging.getLogger(name)