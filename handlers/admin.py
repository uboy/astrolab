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
    MSG_ACTION_CANCELLED, MSG_RETURNING_TO_MENU
)
from keyboards.menus import main_menu

router = Router()

class AdminStates(StatesGroup):
    admin_state = State()
    all_states = State()


# -----------------------------
# Проверка админа
# -----------------------------
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMINS


# -----------------------------
# Главное меню админки
# -----------------------------
@router.message(F.text == BTN_ADMIN)
async def admin_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return
    await state.set_state(AdminStates.admin_state)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_USER_STATS), KeyboardButton(text=BTN_RESET_LIMITS)],
            [KeyboardButton(text=BTN_CANCEL)]
        ],
        resize_keyboard=True
    )
    await message.answer(MSG_ADMIN_MENU, reply_markup=keyboard)


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

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_ADMIN), KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True
    )

    for idx, chunk in enumerate(chunks):
        is_last = idx == len(chunks) - 1
        await message.answer(
            MSG_USER_STATS_HEADER.format(stats=chunk),
            reply_markup=keyboard if is_last else ReplyKeyboardRemove()
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

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_ADMIN), KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True
    )
    await message.answer(MSG_LIMITS_RESET, reply_markup=keyboard)


# -----------------------------
# Отмена действия
# -----------------------------
@router.message(F.text == BTN_CANCEL, StateFilter(AdminStates.admin_state))
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
