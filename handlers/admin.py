from aiogram import Router, F, Bot
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from utils.json_db import read_json, write_json
from utils.config import settings
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
import asyncio
from utils.constants import (
    BTN_ADMIN, BTN_CANCEL,
    MSG_NO_ACCESS, MSG_NO_COMMAND_ACCESS, MSG_ADMIN_MENU,
    MSG_NO_USERS,
    MSG_ACTION_CANCELLED, MSG_RETURNING_TO_MENU,
    BTN_ADMIN_BROADCAST, MSG_ADMIN_BROADCAST_ASK, MSG_ADMIN_BROADCAST_DONE,
    BTN_ADMIN_USERS, BTN_ADMIN_NEXT_PAGE, BTN_ADMIN_PREV_PAGE, BTN_ADMIN_BACK_USERS,
    BTN_ADMIN_USER_INFO, BTN_ADMIN_USER_HISTORY, BTN_ADMIN_USER_RESET,
    BTN_ADMIN_USER_SET_BALANCE,
    BTN_ADMIN_USER_SUBSCRIBE, BTN_ADMIN_USER_UNSUBSCRIBE, BTN_ADMIN_USER_SET_TIME, BTN_ADMIN_USER_DELETE,
    BTN_ADMIN_USER_SEND,
    MSG_ADMIN_TIME_OK, MSG_ADMIN_INVALID_TIME, MSG_ADMIN_NO_USER,
    MSG_ADMIN_USER_BALANCE_PROMPT, MSG_ADMIN_USER_BALANCE_SET,
    BTN_YES, BTN_NO, BTN_ADMIN_SETTINGS, BTN_ADMIN_LOGS,
    BTN_ADMIN_SUBSCRIBED, BTN_ADMIN_SEND_SUBS, BTN_ADMIN_PRICES, BTN_ADMIN_COMPANY_PARAMS, BTN_ADMIN_ABOUT_BOT,
    BTN_ADMIN_COMPANY_PARAMS_TEMPLATE,
    MSG_ADMIN_COMPANY_PARAMS_PROMPT, MSG_ADMIN_COMPANY_PARAMS_SAVED, MSG_ADMIN_COMPANY_PARAMS_TEMPLATE
)
from keyboards.menus import menu_for
from utils.user_helpers import save_user
from utils.subscription_scheduler import send_pending_subscriptions
from utils.prices import get_prices, set_price

router = Router()

PAGE_SIZE = 5


class AdminStates(StatesGroup):
    home = State()
    browsing_users = State()
    user_actions = State()
    waiting_update_time_user = State()
    waiting_set_balance_user = State()
    waiting_broadcast = State()
    waiting_delete_confirm = State()
    waiting_user_message = State()
    waiting_price = State()
    waiting_company_params = State()


# -----------------------------
# Проверка админа
# -----------------------------
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMINS


def _admin_keyboard(extra_buttons=None):
    rows = [
        [KeyboardButton(text=BTN_ADMIN_USERS), KeyboardButton(text=BTN_ADMIN_SUBSCRIBED)],
        [KeyboardButton(text=BTN_ADMIN_SEND_SUBS), KeyboardButton(text=BTN_ADMIN_BROADCAST)],
        [KeyboardButton(text=BTN_ADMIN_PRICES), KeyboardButton(text=BTN_ADMIN_COMPANY_PARAMS)],
        [KeyboardButton(text=BTN_ADMIN_SETTINGS), KeyboardButton(text=BTN_ADMIN_LOGS)],
        [KeyboardButton(text=BTN_ADMIN_ABOUT_BOT)],
        [KeyboardButton(text=BTN_CANCEL)]
    ]
    if extra_buttons:
        rows.insert(0, [KeyboardButton(text=btn) for btn in extra_buttons])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def _company_params_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADMIN_COMPANY_PARAMS_TEMPLATE)],
            [KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def _user_action_keyboard(sub_active: bool):
    sub_button = BTN_ADMIN_USER_UNSUBSCRIBE if sub_active else BTN_ADMIN_USER_SUBSCRIBE
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADMIN_USER_INFO), KeyboardButton(text=BTN_ADMIN_USER_HISTORY)],
            [KeyboardButton(text=BTN_ADMIN_USER_RESET), KeyboardButton(text=BTN_ADMIN_USER_SET_BALANCE)],
            [KeyboardButton(text=sub_button)],
            [KeyboardButton(text=BTN_ADMIN_USER_SET_TIME), KeyboardButton(text=BTN_ADMIN_USER_SEND)],
            [KeyboardButton(text=BTN_ADMIN_USER_DELETE)],
            [KeyboardButton(text=BTN_ADMIN_BACK_USERS)]
        ],
        resize_keyboard=True
    )


def _sorted_users(users: dict) -> list:
    def sort_key(item):
        _, data = item
        return data.get("last_seen", "")
    return sorted(users.items(), key=sort_key, reverse=True)


def _parse_user_button(text: str) -> str | None:
    if "|" in text:
        candidate = text.split("|", 1)[0].strip()
        if candidate.isdigit():
            return candidate
    if text.strip().isdigit():
        return text.strip()
    return None


async def _show_users_page(message: Message, state: FSMContext, page: int = 0, only_subscribed: bool = False):
    users = await read_json("data/users.json")
    changed = False
    for uid, data in users.items():
        profile = data.get("profile") or {}
        profile.setdefault("first_name", "")
        profile.setdefault("last_name", "")
        profile.setdefault("username", "")
        profile.setdefault("language_code", "")
        profile.setdefault("is_premium", None)
        profile.setdefault("phone_number", None)
        data["profile"] = profile
        sub = data.get("subscription") or {}
        sub.setdefault("active", False)
        sub.setdefault("time", "13:00")
        sub.setdefault("birthdate", None)
        sub.setdefault("last_sent", None)
        data["subscription"] = sub
        users[uid] = data
        changed = True
    if changed:
        await write_json("data/users.json", users)
    if not users:
        await message.answer(MSG_NO_USERS, reply_markup=_admin_keyboard())
        return

    if only_subscribed:
        users = {uid: data for uid, data in users.items() if data.get("subscription", {}).get("active")}
        if not users:
            await message.answer("Нет активных подписок.", reply_markup=_admin_keyboard())
            return

    sorted_users = _sorted_users(users)
    total = len(sorted_users)
    max_page = max(0, (total - 1) // PAGE_SIZE)
    page = max(0, min(page, max_page))
    start = page * PAGE_SIZE
    slice_users = sorted_users[start:start + PAGE_SIZE]

    rows = []
    for uid, data in slice_users:
        name = (data.get("profile") or {}).get("first_name") or "Без имени"
        rows.append([KeyboardButton(text=f"{uid} | {name}")])

    nav_row = []
    if page > 0:
        nav_row.append(KeyboardButton(text=BTN_ADMIN_PREV_PAGE))
    if start + PAGE_SIZE < total:
        nav_row.append(KeyboardButton(text=BTN_ADMIN_NEXT_PAGE))
    if nav_row:
        rows.append(nav_row)

    rows.append([KeyboardButton(text=BTN_ADMIN_BROADCAST), KeyboardButton(text=BTN_CANCEL)])

    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    await state.update_data(user_list=[uid for uid, _ in sorted_users], page=page, only_subscribed=only_subscribed)
    title = "Подписчики" if only_subscribed else "Пользователи"
    await message.answer(f"{title}\nВсего: {total}\nСтраница {page + 1}/{max_page + 1}", reply_markup=keyboard)


async def _send_user_summary(message: Message, user_id: str, user_data: dict, state: FSMContext):
    sub = user_data.get("subscription") or {}
    sub_status = "активна" if sub.get("active") else "не активна"
    sub_time = sub.get("time", "-")
    sub_birth = sub.get("birthdate", "-")
    sub_last = sub.get("last_sent", "-")
    premium = user_data.get("premium") or {}
    premium_status = "активен" if premium.get("active") else "не активен"
    premium_until = premium.get("until", "-")
    profile = user_data.get("profile") or {}
    profile_fields = []
    for key, label in [("first_name", "Имя"), ("last_name", "Фамилия"), ("username", "Username"), ("language_code", "Язык"), ("is_premium", "Premium"), ("phone_number", "Телефон")]:
        val = profile.get(key)
        if val is not None and val != "":
            if key == "username":
                val = f"@{val}"
            profile_fields.append(f"{label}: {val}")
    profile_text = "; ".join(profile_fields) if profile_fields else "Профиль: -"

    balance = f"Free: {user_data.get('free_count', 0)}, Paid: {user_data.get('paid_count', 0)}"
    last_seen = user_data.get("last_seen", "-")
    first_seen = user_data.get("first_seen", "-")
    history_len = len(user_data.get("history", []))
    actions_len = len(user_data.get("actions", []))
    total_paid = _total_paid(user_data)
    await message.answer(
        f"👤 Пользователь {user_id}\n{profile_text}\n"
        f"Баланс: {balance}, всего куплено: {total_paid}\n"
        f"Обращений всего: {history_len}, записей действий: {actions_len}\n"
        f"Первое появление: {first_seen}\nПоследняя активность: {last_seen}\n"
        f"Подписка: {sub_status} (время {sub_time}, дата {sub_birth}, последнее {sub_last})\n"
        f"Премиум: {premium_status} (до {premium_until})",
        reply_markup=_user_action_keyboard(sub.get('active', False))
    )
    await state.update_data(selected_user=user_id)


def _format_actions(user: dict, limit: int = 20) -> str:
    actions = user.get("actions", [])[-limit:]
    if not actions:
        return "Действия отсутствуют."
    parts = []
    for action in actions:
        ts = action.get("ts", "-")
        feat = action.get("feature", "-")
        details = action.get("details")
        parts.append(f"{ts} — {feat} — {details}")
    return "\n".join(parts)


def _total_paid(user: dict) -> int:
    total = 0
    for action in user.get("actions", []):
        if action.get("feature") == "payment":
            try:
                total += int(action.get("details", {}).get("amount", 0))
            except Exception:
                continue
    return total


# -----------------------------
# Главное меню админки
# -----------------------------
@router.message(F.text == BTN_ADMIN)
async def admin_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS, reply_markup=ReplyKeyboardRemove())
        return
    await state.set_state(AdminStates.home)
    await message.answer("Админка: выберите раздел.", reply_markup=_admin_keyboard())


# -----------------------------
# Главный экран админки
# -----------------------------
@router.message(AdminStates.home)
async def admin_home(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS, reply_markup=ReplyKeyboardRemove())
        return

    text = message.text.strip()
    if text == BTN_CANCEL:
        await state.clear()
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
        await message.answer(MSG_RETURNING_TO_MENU, reply_markup=menu_for(message.from_user.id))
        return

    if text == BTN_ADMIN_USERS:
        await state.set_state(AdminStates.browsing_users)
        await _show_users_page(message, state, page=0, only_subscribed=False)
        return

    if text == BTN_ADMIN_SUBSCRIBED:
        await state.set_state(AdminStates.browsing_users)
        await _show_users_page(message, state, page=0, only_subscribed=True)
        return

    if text == BTN_ADMIN_SEND_SUBS:
        await message.answer("Отправляю подписанный контент всем активным подписчикам...")
        sent = await send_pending_subscriptions(message.bot, force=True)
        await message.answer(f"Разослано подписчикам: {sent}", reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_PRICES:
        prices = await get_prices()
        text_lines = [f"{k}: {v} у.е" for k, v in prices.items()]
        await state.set_state(AdminStates.waiting_price)
        await message.answer("Текущие цены:\n" + "\n".join(text_lines) + "\nВведите: название цена (например, horoscope 2)", reply_markup=_admin_keyboard())
        return

    if text == BTN_ADMIN_BROADCAST:
        await state.set_state(AdminStates.waiting_broadcast)
        await message.answer(MSG_ADMIN_BROADCAST_ASK, reply_markup=_admin_keyboard())
        return

    if text == BTN_ADMIN_SETTINGS:
        from utils.config import settings
        settings_text = (
            f"⚙️ Настройки бота:\n"
            f"OLLAMA_URL: {getattr(settings, 'OLLAMA_URL', '-')}\n"
            f"OLLAMA_MODEL: {getattr(settings, 'OLLAMA_MODEL', '-')}\n"
            f"OLLAMA_VISION_MODEL: {getattr(settings, 'OLLAMA_VISION_MODEL', '-')}\n"
            f"RATE_LIMIT_PER_MIN: {getattr(settings, 'RATE_LIMIT_PER_MIN', '-')}\n"
            f"RATE_LIMIT_PER_HOUR: {getattr(settings, 'RATE_LIMIT_PER_HOUR', '-')}\n"
            f"FREE_MESSAGES_COUNT: {getattr(settings, 'FREE_MESSAGES_COUNT', '-')}\n"
            f"ADMINS: {', '.join(map(str, getattr(settings, 'ADMINS', [])))}\n"
            f"LOG_LEVEL: {getattr(settings, 'LOG_LEVEL', '-')}\n"
            f"TIMEZONE: {getattr(settings, 'TIMEZONE', '-')}"
        )
        await message.answer(settings_text, reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_ABOUT_BOT:
        from utils.version import get_bot_version
        await message.answer(f"🤖 Версия бота: {get_bot_version()}", reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_COMPANY_PARAMS:
        from utils.company_params import get_company_params_text
        current_text = await get_company_params_text()
        await state.set_state(AdminStates.waiting_company_params)
        await message.answer(
            MSG_ADMIN_COMPANY_PARAMS_PROMPT.format(text=current_text),
            reply_markup=_company_params_keyboard()
        )
        return

    if text == BTN_ADMIN_LOGS:
        try:
            with open("logs/error.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
            tail = "".join(lines[-100:]) if lines else "Лог пуст."
        except FileNotFoundError:
            tail = "Лог-файл ещё не создан."
        max_chunk = 3500
        content = f"Последние строки error.log:\n{tail}"
        for i in range(0, len(content), max_chunk):
            chunk = content[i:i + max_chunk]
            await message.answer(chunk, reply_markup=_admin_keyboard() if i + max_chunk >= len(content) else ReplyKeyboardRemove())
        return
    await message.answer("Выберите раздел кнопкой.", reply_markup=_admin_keyboard())


# -----------------------------
# Навигация по списку пользователей
# -----------------------------
@router.message(AdminStates.browsing_users)
async def browse_users(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return

    text = message.text.strip()
    if text == BTN_CANCEL:
        await state.clear()
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
        await message.answer(MSG_RETURNING_TO_MENU, reply_markup=menu_for(message.from_user.id))
        return
    data = await state.get_data()
    page = data.get("page", 0)
    only_subscribed = data.get("only_subscribed", False)

    if text == BTN_ADMIN_NEXT_PAGE:
        await _show_users_page(message, state, page + 1, only_subscribed=only_subscribed)
        return
    if text == BTN_ADMIN_PREV_PAGE:
        await _show_users_page(message, state, page - 1, only_subscribed=only_subscribed)
        return
    if text == BTN_ADMIN_BROADCAST:
        await state.set_state(AdminStates.waiting_broadcast)
        await message.answer(MSG_ADMIN_BROADCAST_ASK, reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_SEND_SUBS:
        await message.answer("Отправляю подписанный контент всем активным подписчикам...")
        sent = await send_pending_subscriptions(message.bot, force=True)
        await message.answer(f"Разослано подписчикам: {sent}", reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_PRICES:
        prices = await get_prices()
        text_lines = [f"{k}: {v} у.е" for k, v in prices.items()]
        await state.set_state(AdminStates.waiting_price)
        await message.answer("Текущие цены:\n" + "\n".join(text_lines) + "\nВведите: название цена (например, horoscope 2)", reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_SETTINGS:
        from utils.config import settings
        settings_text = (
            f"⚙️ Настройки бота:\n"
            f"OLLAMA_URL: {getattr(settings, 'OLLAMA_URL', '-')}\n"
            f"OLLAMA_MODEL: {getattr(settings, 'OLLAMA_MODEL', '-')}\n"
            f"OLLAMA_VISION_MODEL: {getattr(settings, 'OLLAMA_VISION_MODEL', '-')}\n"
            f"RATE_LIMIT_PER_MIN: {getattr(settings, 'RATE_LIMIT_PER_MIN', '-')}\n"
            f"RATE_LIMIT_PER_HOUR: {getattr(settings, 'RATE_LIMIT_PER_HOUR', '-')}\n"
            f"FREE_MESSAGES_COUNT: {getattr(settings, 'FREE_MESSAGES_COUNT', '-')}\n"
            f"ADMINS: {', '.join(map(str, getattr(settings, 'ADMINS', [])))}\n"
            f"LOG_LEVEL: {getattr(settings, 'LOG_LEVEL', '-')}\n"
            f"TIMEZONE: {getattr(settings, 'TIMEZONE', '-')}"
        )
        await message.answer(settings_text, reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_ABOUT_BOT:
        from utils.version import get_bot_version
        await message.answer(f"🤖 Версия бота: {get_bot_version()}", reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_COMPANY_PARAMS:
        from utils.company_params import get_company_params_text
        current_text = await get_company_params_text()
        await state.set_state(AdminStates.waiting_company_params)
        await message.answer(
            MSG_ADMIN_COMPANY_PARAMS_PROMPT.format(text=current_text),
            reply_markup=_company_params_keyboard()
        )
        return
    if text == BTN_ADMIN_LOGS:
        try:
            with open("logs/error.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
            tail = "".join(lines[-100:]) if lines else "Лог пуст."
        except FileNotFoundError:
            tail = "Лог-файл ещё не создан."
        await message.answer(f"Последние строки error.log:\n{tail}", reply_markup=_admin_keyboard())
        return
    if text == BTN_ADMIN_USERS:
        await state.update_data(only_subscribed=False)
        await _show_users_page(message, state, page=0, only_subscribed=False)
        return
    if text == BTN_ADMIN_SUBSCRIBED:
        await state.update_data(only_subscribed=True)
        await _show_users_page(message, state, page=0, only_subscribed=True)
        return

    user_id = _parse_user_button(text)
    if not user_id:
        await message.answer("Выберите пользователя кнопкой или используйте навигацию.", reply_markup=_admin_keyboard())
        return

    users = await read_json("data/users.json")
    user_data = users.get(user_id)
    if not user_data:
        await message.answer(MSG_ADMIN_NO_USER.format(user_id=user_id), reply_markup=_admin_keyboard())
        return

    await state.set_state(AdminStates.user_actions)
    await state.update_data(selected_user=user_id, page=page)
    await _send_user_summary(message, user_id, user_data, state)


# -----------------------------
# Действия над выбранным пользователем
# -----------------------------
@router.message(AdminStates.user_actions)
async def user_actions(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return

    text = message.text.strip()
    if text == BTN_CANCEL:
        await state.clear()
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
        await message.answer(MSG_RETURNING_TO_MENU, reply_markup=menu_for(message.from_user.id))
        return
    data = await state.get_data()
    user_id = data.get("selected_user")
    if not user_id:
        await state.set_state(AdminStates.browsing_users)
        await _show_users_page(message, state)
        return

    users = await read_json("data/users.json")
    user = users.get(user_id)
    if not user:
        await message.answer(MSG_ADMIN_NO_USER.format(user_id=user_id), reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.browsing_users)
        return

    if text == BTN_ADMIN_USER_INFO:
        await _send_user_summary(message, user_id, user, state)
        return

    if text == BTN_ADMIN_USER_HISTORY:
        history_text = _format_actions(user)
        await message.answer(f"История действий пользователя {user_id}:\n{history_text}", reply_markup=_user_action_keyboard(user.get('subscription', {}).get('active', False)))
        return

    if text == BTN_ADMIN_USER_RESET:
        user["free_count"] = settings.FREE_MESSAGES_COUNT
        user["paid_count"] = 0
        users[user_id] = user
        await write_json("data/users.json", users)
        await message.answer(
            f"✅ Лимиты пользователя {user_id} сброшены: Free={settings.FREE_MESSAGES_COUNT}, Paid=0.",
            reply_markup=_user_action_keyboard(user.get('subscription', {}).get('active', False))
        )
        return

    if text == BTN_ADMIN_USER_SET_BALANCE:
        await state.set_state(AdminStates.waiting_set_balance_user)
        await message.answer(
            MSG_ADMIN_USER_BALANCE_PROMPT,
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_CANCEL)]], resize_keyboard=True)
        )
        return

    if text == BTN_ADMIN_USER_SUBSCRIBE:
        sub = user.get("subscription") or {}
        sub["active"] = True
        sub.setdefault("time", "13:00")
        user["subscription"] = sub
        users[user_id] = user
        await write_json("data/users.json", users)
        await _send_user_summary(message, user_id, user, state)
        return

    if text == BTN_ADMIN_USER_UNSUBSCRIBE:
        sub = user.get("subscription") or {}
        sub["active"] = False
        sub["last_sent"] = None
        user["subscription"] = sub
        users[user_id] = user
        await write_json("data/users.json", users)
        await _send_user_summary(message, user_id, user, state)
        return

    if text == BTN_ADMIN_USER_SET_TIME:
        await state.set_state(AdminStates.waiting_update_time_user)
        await message.answer("Введите время ЧЧ:ММ (любое, например 14:30) для пользователя.", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_CANCEL)]], resize_keyboard=True))
        return

    if text == BTN_ADMIN_USER_SEND:
        await state.set_state(AdminStates.waiting_user_message)
        await message.answer("Введите текст для немедленной отправки пользователю.", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_CANCEL)]], resize_keyboard=True))
        return

    if text == BTN_ADMIN_USER_DELETE:
        await state.set_state(AdminStates.waiting_delete_confirm)
        await message.answer(f"Удалить пользователя {user_id}? ({BTN_YES}/{BTN_NO})", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=BTN_YES), KeyboardButton(text=BTN_NO)]], resize_keyboard=True))
        return

    if text == BTN_ADMIN_BACK_USERS:
        await state.set_state(AdminStates.browsing_users)
        await _show_users_page(message, state, page=data.get("page", 0))
        return

    await message.answer("Выберите действие кнопкой.", reply_markup=_user_action_keyboard(user.get('subscription', {}).get('active', False)))


# -----------------------------
# Изменение времени подписки
# -----------------------------
@router.message(AdminStates.waiting_update_time_user)
async def admin_set_time(message: Message, state: FSMContext):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.set_state(AdminStates.user_actions)
        data = await state.get_data()
        user_id = data.get("selected_user")
        users = await read_json("data/users.json")
        user = users.get(user_id, {})
        await _send_user_summary(message, user_id, user, state)
        return

    data = await state.get_data()
    user_id = data.get("selected_user")
    users = await read_json("data/users.json")
    user = users.get(user_id)
    if not user:
        await message.answer(MSG_ADMIN_NO_USER.format(user_id=user_id), reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.browsing_users)
        return

    try:
        hours, minutes = map(int, message.text.strip().split(":"))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError
    except Exception:
        await message.answer(MSG_ADMIN_INVALID_TIME)
        return

    hours = max(0, min(23, hours))
    minutes = max(0, min(59, minutes))
    normalized_time = f"{hours:02d}:{minutes:02d}"

    sub = user.get("subscription") or {}
    sub.setdefault("active", False)
    sub["time"] = normalized_time
    user["subscription"] = sub
    users[user_id] = user
    await write_json("data/users.json", users)
    await state.set_state(AdminStates.user_actions)
    await message.answer(MSG_ADMIN_TIME_OK.format(user_id=user_id, time=normalized_time), reply_markup=_user_action_keyboard(sub.get('active', False)))


# -----------------------------
# Изменение free/paid баланса
# -----------------------------
@router.message(AdminStates.waiting_set_balance_user)
async def admin_set_user_balance(message: Message, state: FSMContext):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.set_state(AdminStates.user_actions)
        data = await state.get_data()
        user_id = data.get("selected_user")
        users = await read_json("data/users.json")
        user = users.get(user_id, {})
        await _send_user_summary(message, user_id, user, state)
        return

    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer(MSG_ADMIN_USER_BALANCE_PROMPT)
        return
    try:
        free_count = max(0, int(parts[0]))
        paid_count = max(0, int(parts[1]))
    except ValueError:
        await message.answer("Оба значения должны быть целыми числами.")
        return

    data = await state.get_data()
    user_id = data.get("selected_user")
    users = await read_json("data/users.json")
    user = users.get(user_id)
    if not user:
        await message.answer(MSG_ADMIN_NO_USER.format(user_id=user_id), reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.browsing_users)
        return

    user["free_count"] = free_count
    user["paid_count"] = paid_count
    users[user_id] = user
    await write_json("data/users.json", users)
    await state.set_state(AdminStates.user_actions)
    await message.answer(
        MSG_ADMIN_USER_BALANCE_SET.format(user_id=user_id, free=free_count, paid=paid_count),
        reply_markup=_user_action_keyboard(user.get('subscription', {}).get('active', False))
    )


# -----------------------------
# Немедленная отправка сообщения выбранному пользователю
# -----------------------------
@router.message(AdminStates.waiting_user_message)
async def admin_send_user_message(message: Message, state: FSMContext, bot: Bot):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.set_state(AdminStates.user_actions)
        data = await state.get_data()
        user_id = data.get("selected_user")
        users = await read_json("data/users.json")
        user = users.get(user_id, {})
        await _send_user_summary(message, user_id, user, state)
        return

    data = await state.get_data()
    user_id = data.get("selected_user")
    if not user_id:
        await state.set_state(AdminStates.browsing_users)
        await _show_users_page(message, state)
        return

    text = message.text
    try:
        await bot.send_message(int(user_id), text)
        await message.answer(f"Сообщение отправлено пользователю {user_id}.", reply_markup=_user_action_keyboard(True))
    except Exception:
        await message.answer(f"Не удалось отправить сообщение пользователю {user_id}.", reply_markup=_user_action_keyboard(True))
    await state.set_state(AdminStates.user_actions)


# -----------------------------
# Удаление пользователя
# -----------------------------
@router.message(AdminStates.waiting_delete_confirm)
async def admin_delete_user(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    data = await state.get_data()
    user_id = data.get("selected_user")

    if text == BTN_CANCEL.lower() or text == BTN_NO.lower():
        await state.set_state(AdminStates.user_actions)
        users = await read_json("data/users.json")
        user = users.get(user_id, {})
        await _send_user_summary(message, user_id, user, state)
        return

    if text == BTN_YES.lower():
        users = await read_json("data/users.json")
        if user_id in users:
            users.pop(user_id, None)
            await write_json("data/users.json", users)
        await message.answer(f"Пользователь {user_id} удалён.", reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.browsing_users)
        await _show_users_page(message, state, page=0)
        return

    await message.answer(f"Подтвердите {BTN_YES} или {BTN_NO}.")


# -----------------------------
# Разослать уведомление всем подписчикам
# -----------------------------
@router.message(AdminStates.waiting_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.set_state(AdminStates.browsing_users)
        await _show_users_page(message, state, page=0)
        return

    text = message.text.strip()
    users = await read_json("data/users.json")
    count = 0
    for uid, user in users.items():
        sub = user.get("subscription") or {}
        if not sub.get("active"):
            continue
        try:
            await bot.send_message(int(uid), text)
            count += 1
        except Exception:
            continue

    await message.answer(MSG_ADMIN_BROADCAST_DONE.format(count=count), reply_markup=_admin_keyboard())
    await state.set_state(AdminStates.browsing_users)
    await _show_users_page(message, state, page=0)


# -----------------------------
# Установка цены
# -----------------------------
@router.message(AdminStates.waiting_price)
async def admin_set_price(message: Message, state: FSMContext):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=_admin_keyboard())
        return
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("Используйте формат: название цена (например, horoscope 2)", reply_markup=_admin_keyboard())
        return
    feature, price_str = parts
    try:
        price_val = int(price_str)
    except ValueError:
        await message.answer("Цена должна быть числом.", reply_markup=_admin_keyboard())
        return
    await set_price(feature, price_val)
    prices = await get_prices()
    text_lines = [f"{k}: {v}" for k, v in prices.items()]
    await message.answer("Цены обновлены:\n" + "\n".join(text_lines), reply_markup=_admin_keyboard())
    await state.clear()


# -----------------------------
# Обновление параметров компании
# -----------------------------
@router.message(AdminStates.waiting_company_params)
async def admin_set_company_params(message: Message, state: FSMContext):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=_admin_keyboard())
        return
    if message.text.strip() == BTN_ADMIN_COMPANY_PARAMS_TEMPLATE:
        from utils.constants import DEFAULT_COMPANY_PARAMS_TEXT
        await message.answer(MSG_ADMIN_COMPANY_PARAMS_TEMPLATE, reply_markup=_company_params_keyboard())
        await message.answer(DEFAULT_COMPANY_PARAMS_TEXT, reply_markup=_company_params_keyboard())
        return
    text = message.text.strip()
    if not text:
        await message.answer("Текст не должен быть пустым. Введите новый текст или «Отмена».", reply_markup=_company_params_keyboard())
        return
    from utils.company_params import set_company_params_text
    await set_company_params_text(text)
    await message.answer(MSG_ADMIN_COMPANY_PARAMS_SAVED, reply_markup=_admin_keyboard())
    await state.clear()


# -----------------------------
# Отмена действия
# -----------------------------
@router.message(
    F.text == BTN_CANCEL,
    StateFilter(AdminStates.home, AdminStates.browsing_users, AdminStates.user_actions, AdminStates.waiting_update_time_user, AdminStates.waiting_set_balance_user, AdminStates.waiting_broadcast, AdminStates.waiting_delete_confirm, AdminStates.waiting_user_message, AdminStates.waiting_price, AdminStates.waiting_company_params)
)
async def admin_cancel(message: Message, state: FSMContext):
    await state.clear()
    if is_admin(message.from_user.id):
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
        await message.answer(MSG_RETURNING_TO_MENU, reply_markup=menu_for(message.from_user.id))
    else:
        await message.answer(MSG_NO_COMMAND_ACCESS, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
        await message.answer(MSG_RETURNING_TO_MENU, reply_markup=menu_for(message.from_user.id))
