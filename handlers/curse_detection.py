#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.curses_data import CURSES, RITUALS
from utils.constants import (
    BTN_CURSE_DETECTION, BTN_BACK, BTN_YES, BTN_NO,
    MSG_CURSE_DETECTION_RESULT, MSG_CURSE_RITUAL, MSG_CURSE_REMAINS,
    MSG_RETURNED_TO_MENU, MSG_INVALID_DECISION
)
from keyboards.menus import main_menu
import random

router = Router()

class CurseDetectionStates(StatesGroup):
    waiting_decision = State()


# -----------------------------
# Старт определения проклятия
# -----------------------------
@router.message(F.text == BTN_CURSE_DETECTION, StateFilter(None))
async def start_curse_detection(message: Message, state: FSMContext):
    # Случайно выбираем проклятие
    selected_curse = random.choice(CURSES)
    
    # Сохраняем выбранное проклятие в состоянии
    await state.update_data(curse=selected_curse)
    await state.set_state(CurseDetectionStates.waiting_decision)
    
    # Создаем клавиатуру с вариантами ответа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_YES), KeyboardButton(text=BTN_NO)],
            [KeyboardButton(text=BTN_BACK)]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        MSG_CURSE_DETECTION_RESULT.format(curse=selected_curse),
        reply_markup=keyboard
    )


# -----------------------------
# Обработка решения пользователя
# -----------------------------
@router.message(CurseDetectionStates.waiting_decision)
async def handle_curse_decision(message: Message, state: FSMContext):
    text = message.text.strip()
    
    if text.lower() == BTN_BACK.lower():
        await state.clear()
        await message.answer(MSG_RETURNED_TO_MENU, reply_markup=main_menu)
        return
    
    if text.lower() in [BTN_YES.lower(), "yes"]:
        # Пользователь хочет снять проклятие
        data = await state.get_data()
        curse = data.get("curse", "")
        
        # Случайно выбираем обряд
        selected_ritual = random.choice(RITUALS)
        
        await message.answer(
            MSG_CURSE_RITUAL.format(ritual=selected_ritual),
            reply_markup=main_menu
        )
        await state.clear()
        return
    
    if text.lower() in [BTN_NO.lower(), "no"]:
        # Пользователь не хочет снимать проклятие
        await message.answer(MSG_CURSE_REMAINS, reply_markup=main_menu)
        await state.clear()
        return
    
    # Если введен неизвестный текст, просим выбрать из предложенных вариантов
    await message.answer(MSG_INVALID_DECISION)
