from aiogram import Router, F, Bot
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_PAYMENT, BTN_ABOUT, BTN_CANCEL, BTN_HOROSCOPE, BTN_COMPATIBILITY, BTN_NUMEROLOGY, BTN_PHOTO_DESTINY, BTN_CURSE_REMOVAL, BTN_CURSE_DETECTION,
    BTN_PAYMENT_AMOUNT_5, BTN_PAYMENT_AMOUNT_10, BTN_PAYMENT_AMOUNT_15, BTN_PAYMENT_AMOUNT_20,
    BTN_PAYMENT_METHOD_PIGEONS, BTN_PAYMENT_METHOD_FINGER, BTN_PAYMENT_METHOD_COINS,
    PAYMENT_AMOUNTS, PAYMENT_METHODS,
    MSG_PAYMENT_GREETING, MSG_PAYMENT_CANCELLED, MSG_RETURNING_TO_MENU,
    MSG_INVALID_AMOUNT, MSG_INVALID_PAYMENT_METHOD,
    MSG_PAYMENT_PROCESSING, MSG_PAYMENT_SUCCESS, PAYMENT_FAIL_MESSAGES,
    MSG_ABOUT_COMPANY, MSG_FALLBACK_GREETING,
    ALL_MENU_BUTTONS, DEFAULT_USER_NAME, DEFAULT_USER_NAME_LOWER
)
from utils.user_helpers import get_user_name, get_user, save_user
from utils.message_helpers import return_to_main_menu
from keyboards.menus import main_menu, payment_type_menu
import asyncio
import random

router = Router()

class PaymentStates(StatesGroup):
    choosing_amount = State()
    choosing_method = State()


# -----------------------------
# Старт оплаты
# -----------------------------
@router.message(F.text == BTN_PAYMENT, StateFilter(None))
async def payment_start(message: Message, state: FSMContext):
    await state.clear()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_PAYMENT_AMOUNT_5), KeyboardButton(text=BTN_PAYMENT_AMOUNT_10)],
            [KeyboardButton(text=BTN_PAYMENT_AMOUNT_15), KeyboardButton(text=BTN_PAYMENT_AMOUNT_20)],
            [KeyboardButton(text=BTN_CANCEL)]
        ],
        resize_keyboard=True
    )
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    await state.set_state(PaymentStates.choosing_amount)
    await message.answer(
        MSG_PAYMENT_GREETING.format(name=user_name),
        reply_markup=keyboard
    )


# -----------------------------
# Выбор количества
# -----------------------------
@router.message(PaymentStates.choosing_amount)
async def choose_amount(message: Message, state: FSMContext):
    if message.text.lower() == BTN_CANCEL.lower():
        await return_to_main_menu(message, state, MSG_PAYMENT_CANCELLED, remove_keyboard=True)
        return

    if message.text not in PAYMENT_AMOUNTS:
        await message.answer(MSG_INVALID_AMOUNT)
        return

    await state.update_data(amount=int(message.text))

    await state.set_state(PaymentStates.choosing_method)
    await message.answer("Выберите способ оплаты:", reply_markup=payment_type_menu)


# -----------------------------
# Выбор метода
# -----------------------------
@router.message(PaymentStates.choosing_method)
async def choose_method(message: Message, state: FSMContext, bot: Bot):
    if message.text.lower() == BTN_CANCEL.lower():
        await return_to_main_menu(message, state, MSG_PAYMENT_CANCELLED, remove_keyboard=True)
        return

    if message.text not in PAYMENT_METHODS:
        await message.answer(MSG_INVALID_PAYMENT_METHOD)
        return

    data = await state.get_data()
    amount = data.get("amount", 0)
    user_id = str(message.from_user.id)

    user = await get_user(message.from_user.id)

    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    except Exception:
        pass

    await message.answer(MSG_PAYMENT_PROCESSING.format(amount=amount, method=message.text))
    await asyncio.sleep(5)

    # 75% шанс успеха
    success = random.choice([True, True, True, False])

    if not success:
        fail_message = PAYMENT_FAIL_MESSAGES.get(message.text, "Оплата не прошла. Попробуйте снова.")
        await return_to_main_menu(message, state, fail_message, remove_keyboard=True)
        return

    # Успех
    user["paid_count"] += amount
    await save_user(message.from_user.id, user)

    balance = f"📊 Бесплатные: {user['free_count']}, 💎 Оплаченные: {user['paid_count']}"
    await message.answer(
        MSG_PAYMENT_SUCCESS.format(amount=amount, balance=balance),
        reply_markup=main_menu
    )
    await state.clear()


# -----------------------------
# О компании
# -----------------------------
@router.message(F.text == BTN_ABOUT)
async def about_company(message: Message):
    await message.answer(MSG_ABOUT_COMPANY, reply_markup=main_menu, parse_mode='HTML')


# -----------------------------
# ФОЛЛБЕК — работает только когда НЕТ состояний
# и НЕ трогает админку/сервисные команды ✅
# -----------------------------
@router.message(StateFilter(None))
async def fallback(message: Message):
    if message.text in ALL_MENU_BUTTONS:
        return  # позволяем другим роутерам поймать

    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME_LOWER)
    services = "\n- ".join([
        BTN_HOROSCOPE, BTN_COMPATIBILITY, BTN_NUMEROLOGY, BTN_PHOTO_DESTINY,
        BTN_CURSE_REMOVAL, BTN_CURSE_DETECTION, BTN_PAYMENT, BTN_ABOUT
    ])

    await message.answer(
        MSG_FALLBACK_GREETING.format(name=user_name, services=services),
        reply_markup=main_menu
    )
