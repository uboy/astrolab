import asyncio
from datetime import datetime, time
from typing import Tuple
from utils.json_db import read_json, write_json
from utils.zodiac import get_zodiac_sign
from utils.ollama import ask_ollama
from utils.logging_config import get_logger
from utils.constants import DEFAULT_USER_NAME

logger = get_logger(__name__)


def _parse_time(value: str) -> time:
    try:
        parts = value.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
    except Exception:
        hour, minute = 13, 0

    hour = max(12, min(15, hour))
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


async def _process_once(bot) -> None:
    users = await read_json("data/users.json")
    if not users:
        return

    now = datetime.now()
    today_iso = now.date().isoformat()
    changed = False

    for uid, user in users.items():
        sub = user.get("subscription") or {}
        if not sub.get("active"):
            continue

        send_time = _parse_time(sub.get("time", "13:00"))
        target_dt = datetime.combine(now.date(), send_time)

        if now.time() < time(12, 0) or now.time() > time(15, 0):
            continue

        if sub.get("last_sent") == today_iso:
            continue

        if now >= target_dt:
            try:
                prompt, title = await _build_horoscope_prompt(user)
                response = await ask_ollama(prompt)
                text = response if response.strip() else title
                await bot.send_message(int(uid), f"{title}\n\n{text}")
                sub["last_sent"] = today_iso
                user["subscription"] = sub
                changed = True
            except Exception as e:
                logger.error(f"Ошибка отправки подписки пользователю {uid}: {e}", exc_info=True)
                continue

    if changed:
        await write_json("data/users.json", users)


async def run_subscription_scheduler(bot) -> None:
    """Фоновой цикл ежедневных гороскопов."""
    while True:
        try:
            await _process_once(bot)
        except Exception as e:
            logger.error(f"Сбой в цикле подписок: {e}", exc_info=True)
        await asyncio.sleep(60)
