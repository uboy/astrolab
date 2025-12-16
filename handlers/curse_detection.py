#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.curses_data import CURSES, RITUALS
from utils.constants import (
    BTN_LUCK_RESET, BTN_BACK, BTN_YES, BTN_NO, BTN_CANCEL,
    MSG_LUCK_RESET_RESULT, MSG_LUCK_RESET_RITUAL, MSG_LUCK_RESET_SKIP,
    MSG_RETURNED_TO_MENU, MSG_INVALID_DECISION, MSG_NO_FREE_PAID, MSG_LUCK_RESET_GREETING
)
from keyboards.menus import main_menu, payment_menu
import random
from handlers.base import PaymentStates
from utils.user_helpers import check_user_limit, log_user_action, save_user
from utils.rate_limit import check_rate_limit
import datetime

router = Router()

class CurseDetectionStates(StatesGroup):
    waiting_decision = State()


# -----------------------------
# Старт перезапуска удачи
# -----------------------------
@router.message(F.text == BTN_LUCK_RESET, StateFilter(None))
async def start_curse_detection(message: Message, state: FSMContext):
    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        #await state.clear()
        await state.set_state(PaymentStates.choosing_amount)
        return
    allowed, wait_msg = check_rate_limit(user, "luck_reset")
    if not allowed:
        await save_user(message.from_user.id, user)
        await message.answer(wait_msg, reply_markup=main_menu)
        return
    # фиксируем использование небесплатной функции без списания лимита
    ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
    rate = user.get("rate", {"minute": [], "hour": []})
    rate.setdefault("minute", []).append(ts)
    rate.setdefault("hour", []).append(ts)
    user["rate"] = rate
    await save_user(message.from_user.id, user)

    # Случайно выбираем забавный сценарий неудачи
    selected_curse = random.choice(CURSES)
    
    # Сохраняем выбранное проклятие в состоянии
    await state.update_data(curse=selected_curse)
    await state.set_state(CurseDetectionStates.waiting_decision)
    
    # Создаем клавиатуру с вариантами ответа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_YES), KeyboardButton(text=BTN_NO)],
            [KeyboardButton(text=BTN_BACK), KeyboardButton(text=BTN_CANCEL)]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"{MSG_LUCK_RESET_GREETING}\n\n" + MSG_LUCK_RESET_RESULT.format(curse=selected_curse),
        reply_markup=keyboard
    )
    await log_user_action(
        message.from_user.id,
        feature="curse_detection_start",
        details={"suggested_curse": selected_curse},
        telegram_user=message.from_user,
    )


# -----------------------------
# Обработка решения пользователя
# -----------------------------
@router.message(CurseDetectionStates.waiting_decision)
async def handle_curse_decision(message: Message, state: FSMContext):
    text = message.text.strip()
    
    if text.lower() in (BTN_BACK.lower(), BTN_CANCEL.lower()):
        await state.clear()
        await message.answer(MSG_RETURNED_TO_MENU, reply_markup=main_menu)
        await log_user_action(
            message.from_user.id,
            feature="curse_detection_decision",
            details={"decision": "back"},
            telegram_user=message.from_user,
        )
        return
    
    if text.lower() in [BTN_YES.lower(), "yes"]:
        # Пользователь хочет снять проклятие
        data = await state.get_data()
        curse = data.get("curse", "")
        
        # Случайно выбираем обряд
        selected_ritual = random.choice(RITUALS)
        
        await message.answer(
            MSG_LUCK_RESET_RITUAL.format(ritual=selected_ritual),
            reply_markup=main_menu, parse_mode='HTML'
        )
        await state.clear()
        await log_user_action(
            message.from_user.id,
            feature="curse_detection_decision",
            details={"decision": "ritual", "curse": curse, "ritual": selected_ritual},
            telegram_user=message.from_user,
        )
        return
    
    if text.lower() in [BTN_NO.lower(), "no"]:
        # Пользователь не хочет снимать проклятие
        await message.answer(MSG_LUCK_RESET_SKIP, reply_markup=main_menu)
        await state.clear()
        await log_user_action(
            message.from_user.id,
            feature="curse_detection_decision",
            details={"decision": "decline"},
            telegram_user=message.from_user,
        )
        return
    
    # Если введен неизвестный текст, просим выбрать из предложенных вариантов
    await message.answer(MSG_INVALID_DECISION)
