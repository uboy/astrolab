import asyncio
from datetime import datetime, time, timedelta
from typing import Tuple
import hashlib
from zoneinfo import ZoneInfo
from utils.config import settings
from utils.json_db import read_json, write_json
from utils.prices import get_prices
from utils.user_helpers import has_balance, decrement_user_limit
from utils.zodiac import get_zodiac_sign
from utils.ollama import ask_ollama
from utils.logging_config import get_logger
from utils.constants import DEFAULT_USER_NAME

logger = get_logger(__name__)


def _detect_tz():
    tz_name = getattr(settings, "TIMEZONE", "") or ""
    if tz_name and tz_name.lower() != "local":
        try:
            return ZoneInfo(tz_name)
        except Exception:
            logger.warning("Не удалось загрузить таймзону %s, используем локальную.", tz_name)
    try:
        return datetime.now().astimezone().tzinfo or ZoneInfo("UTC")
    except Exception:
        return ZoneInfo("UTC")


def _now_local() -> datetime:
    tz = _detect_tz()
    return datetime.now(tz)


def _default_send_time(user_id: str) -> time:
    """
    Детерминированно распределяем пользователей по окну 11:00-19:00.
    """
    window_start = time(hour=11, minute=0)
    window_minutes = 8 * 60  # 11:00-19:00
    uid_bytes = str(user_id).encode()
    h = hashlib.md5(uid_bytes).hexdigest()
    offset = int(h, 16) % window_minutes
    now = _now_local()
    start_dt = datetime.combine(now.date(), window_start, tzinfo=now.tzinfo)
    send_dt = start_dt + timedelta(minutes=offset)
    return send_dt.time()


def _parse_time(value: str) -> time | None:
    try:
        parts = value.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
    except Exception:
        return None

    hour = max(0, min(23, hour))
    minute = max(0, min(59, minute))
    return time(hour=hour, minute=minute)


async def _build_horoscope_prompt(user: dict) -> Tuple[str, str]:
    sub = user.get("subscription") or {}
    birthdate = sub.get("birthdate")
    zodiac_label = "✨ Неизвестный знак"
    if birthdate:
        try:
            dt = datetime.strptime(birthdate, "%d.%m.%Y")
            sign, emoji = get_zodiac_sign(dt.month, dt.day)
            zodiac_label = f"{emoji} {sign}"
            pretty_date = dt.strftime("%d.%m.%Y")
        except Exception:
            pretty_date = birthdate
    else:
        pretty_date = "не указана"

    user_name = (user.get("profile") or {}).get("first_name") or DEFAULT_USER_NAME
    prompt = (
        "Составь короткий ежедневный гороскоп (3-4 абзаца) с дружелюбным юмором и эмодзи. "
        f"Имя: {user_name}. Дата рождения: {pretty_date}. Знак: {zodiac_label}. "
        "Дай общий тон дня, предостережение и маленький совет."
    )
    title = f"Ваш ежедневный гороскоп, {zodiac_label}"
    return prompt, title


async def _process_once(bot, force: bool = False) -> int:
    users = await read_json("data/users.json")
    prices = await get_prices()
    sub_price = prices.get("subscription", 1)
    if not users:
        return 0

    now = _now_local()
    today_iso = now.date().isoformat()
    changed = False
    sent = 0

    for uid, user in users.items():
        sub = user.get("subscription") or {}
        if not sub.get("active"):
            continue

        # Определяем время отправки
        time_raw = sub.get("time")
        parsed_time = _parse_time(time_raw) if time_raw not in (None, "auto", "") else None
        if parsed_time is None:
            send_time = _default_send_time(uid)
        else:
            send_time = parsed_time
        target_dt = datetime.combine(now.date(), send_time, tzinfo=now.tzinfo)

        if sub.get("last_sent") == today_iso and not force:
            continue

        if now >= target_dt or force:
            try:
                if not has_balance(user, sub_price):
                    sub["active"] = False
                    user["subscription"] = sub
                    users[uid] = user
                    try:
                        await bot.send_message(int(uid), f"Подписка остановлена: не хватило {sub_price} у.е на счету.")
                    except Exception:
                        logger.warning("Не удалось уведомить пользователя %s об остановке подписки", uid)
                    changed = True
                    continue

                prompt, title = await _build_horoscope_prompt(user)
                response = await ask_ollama(prompt)
                text = response if response.strip() else title
                await bot.send_message(int(uid), f"{title}\n\n{text}")
                # списываем оплату за отправку
                user = await decrement_user_limit(int(uid), price=sub_price, feature="subscription_send", details={"date": today_iso})
                sub["last_sent"] = today_iso
                user["subscription"] = sub
                users[uid] = user
                changed = True
                sent += 1
            except Exception as e:
                logger.error(f"Ошибка отправки подписки пользователю {uid}: {e}", exc_info=True)
                continue

    if changed:
        await write_json("data/users.json", users)
    return sent


async def run_subscription_scheduler(bot) -> None:
    """Фоновой цикл ежедневных гороскопов."""
    try:
        await _process_once(bot, force=False)
    except Exception as e:
        logger.error(f"Стартовая отправка подписок не удалась: {e}", exc_info=True)
    while True:
        try:
            await _process_once(bot)
        except Exception as e:
            logger.error(f"Сбой в цикле подписок: {e}", exc_info=True)
        await asyncio.sleep(60)


async def send_pending_subscriptions(bot, force: bool = False) -> int:
    """Отправить подписки немедленно (force=True игнорирует отметку за день). Возвращает количество отправленных."""
    try:
        return await _process_once(bot, force=force)
    except Exception as e:
        logger.error(f"Ошибка при ручной рассылке подписок: {e}", exc_info=True)
        return 0
