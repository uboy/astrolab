"""
Утилиты для работы с пользователями
"""

from utils.json_db import read_json, write_json
from utils.config import settings
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from aiogram.types import User as TgUser


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_profile(telegram_user: Optional[TgUser]) -> Dict[str, Any]:
    if not telegram_user:
        return {}

    return {
        "id": telegram_user.id,
        "is_bot": telegram_user.is_bot,
        "first_name": telegram_user.first_name,
        "last_name": telegram_user.last_name,
        "username": telegram_user.username,
        "language_code": telegram_user.language_code,
        "is_premium": getattr(telegram_user, "is_premium", None),
        "phone_number": getattr(telegram_user, "phone_number", None),
        "added_to_attachment_menu": getattr(telegram_user, "added_to_attachment_menu", None),
        "can_join_groups": getattr(telegram_user, "can_join_groups", None),
        "can_read_all_group_messages": getattr(telegram_user, "can_read_all_group_messages", None),
        "supports_inline_queries": getattr(telegram_user, "supports_inline_queries", None),
    }


def _default_subscription() -> Dict[str, Any]:
    return {
        "active": False,
        "time": "13:00",
        "birthdate": None,
        "last_sent": None,
    }


async def get_user(user_id: int, telegram_user: Optional[TgUser] = None) -> Dict[str, Any]:
    """
    Получить пользователя из базы данных или создать нового
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Словарь с данными пользователя
    """
    users = await read_json("data/users.json")
    now_iso = _now_iso()
    user = users.get(
        str(user_id),
        {
            "free_count": settings.FREE_MESSAGES_COUNT,
            "paid_count": 0,
            "history": [],
            "actions": [],
            "rate": {"minute": [], "hour": []},
            "state": None,
            "first_seen": now_iso,
            "last_seen": now_iso,
            "profile": _extract_profile(telegram_user),
        }
    )

    # Гарантируем наличие обязательных полей
    if "history" not in user or not isinstance(user["history"], list):
        user["history"] = []
    if "actions" not in user or not isinstance(user["actions"], list):
        user["actions"] = []
    if "rate" not in user or not isinstance(user["rate"], dict):
        user["rate"] = {"minute": [], "hour": []}
    user.setdefault("state", None)
    # подписка
    subscription = user.get("subscription") or _default_subscription()
    subscription.setdefault("active", False)
    subscription.setdefault("time", "13:00")
    subscription.setdefault("birthdate", None)
    subscription.setdefault("last_sent", None)
    user["subscription"] = subscription

    # first_seen/last_seen
    if not user.get("first_seen"):
        user["first_seen"] = user["history"][0] if user["history"] else now_iso
    user["last_seen"] = now_iso

    # Обновляем профиль, если есть новые данные
    if telegram_user:
        profile = _extract_profile(telegram_user)
        current_profile = user.get("profile") or {}
        current_profile.update(profile)
        user["profile"] = current_profile
    else:
        user.setdefault("profile", {})

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


async def check_user_limit(user_id: int, telegram_user: Optional[TgUser] = None) -> Tuple[Dict[str, Any], bool]:
    """
    Проверить лимит пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Tuple[user_data, has_limit]: Данные пользователя и флаг наличия лимита
    """
    user = await get_user(user_id, telegram_user)
    has_limit = user["free_count"] + user["paid_count"] > 0

    return user, has_limit


async def decrement_user_limit(
    user_id: int,
    price: int = 1,
    feature: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    telegram_user: Optional[TgUser] = None
) -> Dict[str, Any]:
    """
    Уменьшить лимит пользователя на 1 (сначала бесплатные, потом платные)
    
    Args:
        user_id: ID пользователя
        price: цена услуги
    Returns:
        Обновленные данные пользователя
    """
    user = await get_user(user_id, telegram_user)

    if user["free_count"] > 0:
        user["free_count"] = max(0, user["free_count"] - price)
    elif user["paid_count"] > 0:
        user["paid_count"] = max(0, user["paid_count"] - price)

    ts = _now_iso()
    user["history"].append(ts)
    user["state"] = None
    user["last_seen"] = ts

    if feature or details:
        action = {"ts": ts, "feature": feature or "unknown"}
        if details:
            action["details"] = details
        user["actions"].append(action)

    await save_user(user_id, user)
    return user


async def log_user_action(
    user_id: int,
    feature: str,
    details: Optional[Dict[str, Any]] = None,
    telegram_user: Optional[TgUser] = None
) -> Dict[str, Any]:
    """
    Сохранить событие использования функции без списания лимита.
    """
    user = await get_user(user_id, telegram_user)
    ts = _now_iso()
    user["history"].append(ts)
    user["last_seen"] = ts

    action = {"ts": ts, "feature": feature}
    if details:
        action["details"] = details
    user["actions"].append(action)

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
