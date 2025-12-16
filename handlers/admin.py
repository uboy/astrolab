from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from utils.json_db import read_json, write_json
from utils.config import settings
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
import asyncio
from utils.constants import (
    BTN_ADMIN, BTN_USER_STATS, BTN_RESET_LIMITS, BTN_CANCEL,
    MSG_NO_ACCESS, MSG_NO_COMMAND_ACCESS, MSG_ADMIN_MENU,
    MSG_NO_USERS, MSG_LIMITS_RESET, MSG_USER_STATS_HEADER,
    MSG_ACTION_CANCELLED, MSG_RETURNING_TO_MENU,
    BTN_ADMIN_UNSUB, BTN_ADMIN_SET_TIME, MSG_ADMIN_ASK_USER_ID,
    MSG_ADMIN_UNSUB_OK, MSG_ADMIN_TIME_OK, MSG_ADMIN_INVALID_TIME, MSG_ADMIN_NO_USER
)
from keyboards.menus import main_menu

router = Router()

class AdminStates(StatesGroup):
    admin_state = State()
    all_states = State()
    waiting_unsubscribe_user = State()
    waiting_update_time_user = State()


# -----------------------------
# Проверка админа
# -----------------------------
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMINS


def _admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_USER_STATS), KeyboardButton(text=BTN_RESET_LIMITS)],
            [KeyboardButton(text=BTN_ADMIN_UNSUB), KeyboardButton(text=BTN_ADMIN_SET_TIME)],
            [KeyboardButton(text=BTN_CANCEL)]
        ],
        resize_keyboard=True
    )


# -----------------------------
# Главное меню админки
# -----------------------------
@router.message(F.text == BTN_ADMIN)
async def admin_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return
    await state.set_state(AdminStates.admin_state)
    await message.answer(MSG_ADMIN_MENU, reply_markup=_admin_keyboard())


# -----------------------------
# Показ статистики пользователей
# -----------------------------
@router.message(F.text == BTN_USER_STATS)
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return

    users = await read_json("data/users.json")
    if not users:
        await message.answer(MSG_NO_USERS)
        return

    lines = []
    for uid, u in users.items():
        lines.append(
            f"ID: {uid}, Free: {u['free_count']}, Paid: {u['paid_count']}, "
            f"История: {len(u.get('history', []))} обращений, "
            f"Действия: {len(u.get('actions', []))}, "
            f"Первое появление: {u.get('first_seen', '-')}, "
            f"Последняя активность: {u.get('last_seen', '-')}"
        )

    # Делим ответ на части, чтобы не превышать лимит Telegram
    chunks = []
    current_chunk = []
    current_len = 0
    max_len = 3500  # запас относительно лимита 4096

    for line in lines:
        line_len = len(line) + 1  # с учётом переноса строки
        if current_len + line_len > max_len and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_len = line_len
        else:
            current_chunk.append(line)
            current_len += line_len

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    for idx, chunk in enumerate(chunks):
        is_last = idx == len(chunks) - 1
        await message.answer(
            MSG_USER_STATS_HEADER.format(stats=chunk),
            reply_markup=_admin_keyboard() if is_last else ReplyKeyboardRemove()
        )


# -----------------------------
# Сброс лимитов пользователей
# -----------------------------
@router.message(F.text == BTN_RESET_LIMITS)
async def reset_limits(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return

    users = await read_json("data/users.json")
    if not users:
        await message.answer(MSG_NO_USERS)
        return

    for u in users.values():
        u["free_count"] = settings.FREE_MESSAGES_COUNT
        u["paid_count"] = 0
    await write_json("data/users.json", users)

    await message.answer(MSG_LIMITS_RESET, reply_markup=_admin_keyboard())


# -----------------------------
# Отписать пользователя от уведомлений
# -----------------------------
@router.message(F.text == BTN_ADMIN_UNSUB, StateFilter(AdminStates.admin_state))
async def admin_unsubscribe(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_unsubscribe_user)
    await message.answer(MSG_ADMIN_ASK_USER_ID)


@router.message(AdminStates.waiting_unsubscribe_user)
async def admin_unsubscribe_user(message: Message, state: FSMContext):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.admin_state)
        return

    try:
        user_id = str(int(message.text.strip()))
    except ValueError:
        await message.answer(MSG_ADMIN_ASK_USER_ID)
        return

    users = await read_json("data/users.json")
    user = users.get(user_id)
    if not user:
        await message.answer(MSG_ADMIN_NO_USER.format(user_id=user_id), reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.admin_state)
        return

    subscription = user.get("subscription") or {}
    subscription.update({"active": False, "last_sent": None})
    user["subscription"] = subscription
    users[user_id] = user
    await write_json("data/users.json", users)
    await message.answer(MSG_ADMIN_UNSUB_OK.format(user_id=user_id), reply_markup=_admin_keyboard())
    await state.set_state(AdminStates.admin_state)


# -----------------------------
# Изменить время рассылки
# -----------------------------
@router.message(F.text == BTN_ADMIN_SET_TIME, StateFilter(AdminStates.admin_state))
async def admin_set_time_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_update_time_user)
    await message.answer("Введите ID пользователя и время ЧЧ:ММ через пробел (12:00–15:00).")


@router.message(AdminStates.waiting_update_time_user)
async def admin_set_time(message: Message, state: FSMContext):
    if message.text.strip().lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.admin_state)
        return

    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer(MSG_ADMIN_INVALID_TIME)
        return
    user_id, time_str = parts
    try:
        int(user_id)
        hours, minutes = map(int, time_str.split(":"))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError
    except ValueError:
        await message.answer(MSG_ADMIN_INVALID_TIME)
        return

    hours = max(12, min(15, hours))
    minutes = max(0, min(59, minutes))
    normalized_time = f"{hours:02d}:{minutes:02d}"

    users = await read_json("data/users.json")
    user = users.get(user_id)
    if not user:
        await message.answer(MSG_ADMIN_NO_USER.format(user_id=user_id), reply_markup=_admin_keyboard())
        await state.set_state(AdminStates.admin_state)
        return

    subscription = user.get("subscription") or {}
    subscription.setdefault("active", False)
    subscription["time"] = normalized_time
    user["subscription"] = subscription
    users[user_id] = user
    await write_json("data/users.json", users)
    await message.answer(MSG_ADMIN_TIME_OK.format(user_id=user_id, time=normalized_time), reply_markup=_admin_keyboard())
    await state.set_state(AdminStates.admin_state)


# -----------------------------
# Отмена действия
# -----------------------------
@router.message(F.text == BTN_CANCEL, StateFilter(AdminStates.admin_state, AdminStates.waiting_unsubscribe_user, AdminStates.waiting_update_time_user))
async def admin_cancel(message: Message, state: FSMContext):
    await state.clear()
    if is_admin(message.from_user.id):
        await message.answer(MSG_ACTION_CANCELLED, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
        await message.answer(MSG_RETURNING_TO_MENU, reply_markup=main_menu)
    else:
        await message.answer(MSG_NO_COMMAND_ACCESS, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
        await message.answer(MSG_RETURNING_TO_MENU, reply_markup=main_menu)
