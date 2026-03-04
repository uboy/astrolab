from datetime import datetime, timezone
from utils.constants import (
    MSG_RATE_LIMIT, OLLAMA_FEATURES,
    OLLAMA_PER_MIN, OLLAMA_PER_HOUR,
    OTHER_PER_MIN, OTHER_PER_HOUR, PREMIUM_MULTIPLIER
)
from utils.user_helpers import is_premium_active


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def _trim(rate: dict) -> dict:
    now_ts = _now_ts()
    minute_ago = now_ts - 60
    hour_ago = now_ts - 3600
    rate["minute"] = [t for t in rate.get("minute", []) if t > minute_ago]
    rate["hour"] = [t for t in rate.get("hour", []) if t > hour_ago]
    return rate


def check_rate_limit(user: dict, feature: str) -> tuple[bool, str]:
    """
    Проверяем лимит: True если можно продолжать, False и текст если превышен.
    """
    is_ollama = feature in OLLAMA_FEATURES
    per_min = OLLAMA_PER_MIN if is_ollama else OTHER_PER_MIN
    per_hour = OLLAMA_PER_HOUR if is_ollama else OTHER_PER_HOUR

    rate = _trim(user.get("rate", {"minute": [], "hour": []}))
    user["rate"] = rate

    multiplier = PREMIUM_MULTIPLIER if is_premium_active(user) else 1
    per_min *= multiplier
    per_hour *= multiplier

    count_min = len(rate.get("minute", []))
    count_hour = len(rate.get("hour", []))

    if count_min >= per_min or count_hour >= per_hour:
        now_ts = _now_ts()
        wait_min = 0
        if count_min >= per_min and rate["minute"]:
            wait_min = int(rate["minute"][0] + 60 - now_ts)
        wait_hour = 0
        if count_hour >= per_hour and rate["hour"]:
            wait_hour = int(rate["hour"][0] + 3600 - now_ts)
        wait = max(wait_min, wait_hour, 1)
        return False, MSG_RATE_LIMIT.format(wait=wait)

    return True, ""
