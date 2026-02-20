"""
Утилиты для работы с пользователями
"""

from utils.json_db import read_json, write_json
from utils.config import settings
from datetime import datetime
from typing import Dict, Any, Tuple, Optional


async def get_user(user_id: int) -> Dict[str, Any]:
    """
    Получить пользователя из базы данных или создать нового
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Словарь с данными пользователя
    """
    users = await read_json("data/users.json")
    user = users.get(
        str(user_id),
        {
            "free_count": settings.FREE_MESSAGES_COUNT,
            "paid_count": 0,
            "history": [],
            "rate": {"minute": [], "hour": []},
            "state": None
        }
    )
    users[str(user_id)] = user
    await write_json("data/users.json", users)
    return user


async def save_user(user_id: int, user_data: Dict[str, Any]) -> None:
    """
    Сохранить данные пользователя в базу данных
    
    Args:
        user_id: ID пользователя
        user_data: Данные пользователя для сохранения
    """
    users = await read_json("data/users.json")
    users[str(user_id)] = user_data
    await write_json("data/users.json", users)


async def check_user_limit(user_id: int) -> Tuple[Dict[str, Any], bool]:
    """
    Проверить лимит пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Tuple[user_data, has_limit]: Данные пользователя и флаг наличия лимита
    """
    user = await get_user(user_id)
    has_limit = user["free_count"] + user["paid_count"] > 0

    return user, has_limit


async def decrement_user_limit(user_id: int, price: int = 1) -> Dict[str, Any]:
    """
    Уменьшить лимит пользователя на 1 (сначала бесплатные, потом платные)
    
    Args:
        user_id: ID пользователя
        price: цена услуги
    Returns:
        Обновленные данные пользователя
    """
    user = await get_user(user_id)
    
    if user["free_count"] > 0:
        user["free_count"] -= price
    elif user["paid_count"] > 0:
        user["paid_count"] -= price
    
    user["history"].append(datetime.now().isoformat())
    user["state"] = None
    
    await save_user(user_id, user)
    return user


def format_balance(user: Dict[str, Any]) -> str:
    """
    Форматировать баланс пользователя для отображения
    
    Args:
        user: Данные пользователя
        
    Returns:
        Отформатированная строка с балансом
    """
    from utils.constants import MSG_BALANCE_FORMAT
    return MSG_BALANCE_FORMAT.format(
        free_count=user["free_count"],
        paid_count=user["paid_count"]
    )


def get_user_name(user_first_name: Optional[str], default: str = "Друг") -> str:
    """
    Получить имя пользователя или значение по умолчанию
    
    Args:
        user_first_name: Имя пользователя из Telegram
        default: Имя по умолчанию
        
    Returns:
        Имя пользователя
    """
    return user_first_name or default

