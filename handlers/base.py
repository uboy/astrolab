from aiogram import Router, F, Bot
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_PAYMENT, BTN_ABOUT, BTN_CANCEL, BTN_HOROSCOPE, BTN_COMPATIBILITY, BTN_CANDIDATE_COMPATIBILITY, BTN_NUMEROLOGY, BTN_PHOTO_DESTINY, BTN_ZODIAC_QUIZ, BTN_LUCK_RESET,
    BTN_PAYMENT_AMOUNT_5, BTN_PAYMENT_AMOUNT_10, BTN_PAYMENT_AMOUNT_15, BTN_PAYMENT_AMOUNT_20,
    BTN_PAYMENT_METHOD_PIGEONS, BTN_PAYMENT_METHOD_FINGER, BTN_PAYMENT_METHOD_COINS,
    BTN_SUBSCRIBE, BTN_PREMIUM, BTN_PREMIUM_1D, BTN_PREMIUM_2D, BTN_PREMIUM_3D,
    PAYMENT_AMOUNTS, PAYMENT_METHODS,
    MSG_PAYMENT_GREETING, MSG_PAYMENT_CANCELLED, MSG_RETURNING_TO_MENU,
    MSG_INVALID_AMOUNT, MSG_INVALID_PAYMENT_METHOD,
    MSG_PAYMENT_PROCESSING, MSG_PAYMENT_SUCCESS, PAYMENT_FAIL_MESSAGES,
    MSG_ABOUT_COMPANY, MSG_FALLBACK_GREETING,
    ALL_MENU_BUTTONS, DEFAULT_USER_NAME, DEFAULT_USER_NAME_LOWER, MSG_NOT_ENOUGH_FUNDS, PREMIUM_PLANS
)
from utils.user_helpers import get_user_name, get_user, save_user, log_user_action, activate_premium, has_balance, decrement_user_limit, format_balance
from utils.message_helpers import return_to_main_menu
from keyboards.menus import menu_for, payment_type_menu
import asyncio
import random
from utils.prompts import DISCLAIMER
from utils.prices import get_prices
from utils.pricing_helpers import show_price_info

router = Router()

class PaymentStates(StatesGroup):
    choosing_amount = State()
    choosing_method = State()
    choosing_premium = State()


# -----------------------------
# Старт оплаты
# -----------------------------
@router.message(F.text == BTN_PAYMENT, StateFilter(None))
async def payment_start(message: Message, state: FSMContext):
    await state.clear()
    await get_user(message.from_user.id, message.from_user)
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
# Премиум подписка
# -----------------------------
@router.message(F.text == BTN_PREMIUM, StateFilter(None))
async def premium_start(message: Message, state: FSMContext):
    await state.clear()
    prices = await get_prices()
    user = await get_user(message.from_user.id, message.from_user)
    balance_text = format_balance(user)
    min_price = min(prices.get('premium_1d', 5), prices.get('premium_2d', 8), prices.get('premium_3d', 10))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{BTN_PREMIUM_1D} ({prices.get('premium_1d', 5)} у.е)")],
            [KeyboardButton(text=f"{BTN_PREMIUM_2D} ({prices.get('premium_2d', 8)} у.е)")],
            [KeyboardButton(text=f"{BTN_PREMIUM_3D} ({prices.get('premium_3d', 10)} у.е)")],
            [KeyboardButton(text=BTN_CANCEL)]
        ],
        resize_keyboard=True
    )
    await state.set_state(PaymentStates.choosing_premium)
    await message.answer(f"Премиум-подписка: списание по выбранному плану (от {min_price} у.е).\n{balance_text}", reply_markup=keyboard)


@router.message(PaymentStates.choosing_premium)
async def premium_choose(message: Message, state: FSMContext):
    if message.text == BTN_CANCEL:
        await return_to_main_menu(message, state, MSG_PAYMENT_CANCELLED, remove_keyboard=True)
        return

    prices = await get_prices()
    clean_text = (message.text or "").split(" (")[0]
    plan_map = {
        BTN_PREMIUM_1D: ("premium_1d", 1),
        BTN_PREMIUM_2D: ("premium_2d", 2),
        BTN_PREMIUM_3D: ("premium_3d", 3),
    }
    if clean_text not in plan_map:
        await message.answer("Выберите план из списка.")
        return

    key, days = plan_map[clean_text]
    price = prices.get(key, 5)
    user = await get_user(message.from_user.id, message.from_user)
    if not has_balance(user, price):
        await message.answer(MSG_NOT_ENOUGH_FUNDS.format(feature="премиум", price=price, free=user["free_count"], paid=user["paid_count"]), reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return

    # списываем средства
    user = await decrement_user_limit(message.from_user.id, price=price, feature="premium_purchase", details={"days": days}, telegram_user=message.from_user)
    user = activate_premium(user, days)
    await save_user(message.from_user.id, user)
    await state.clear()
    await message.answer(f"Премиум активирован на {days} дн.", reply_markup=menu_for(message.from_user.id))


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

    user = await get_user(message.from_user.id, message.from_user)

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
    await log_user_action(
        message.from_user.id,
        feature="payment",
        details={"amount": amount, "method": message.text},
        telegram_user=message.from_user,
    )

    balance = f"📊 Бесплатные: {user['free_count']}, 💎 Оплаченные: {user['paid_count']}"
    await message.answer(
        MSG_PAYMENT_SUCCESS.format(amount=amount, balance=balance),
        reply_markup=menu_for(message.from_user.id)
    )
    await state.clear()


# -----------------------------
# Глобальная отмена: возвращаем в главное меню из любого состояния
# -----------------------------
# Глобальная отмена: только если нет активных состояний
@router.message(F.text == BTN_CANCEL, StateFilter(None))
async def global_cancel(message: Message, state: FSMContext):
    await return_to_main_menu(message, state, MSG_RETURNING_TO_MENU, remove_keyboard=True)


# -----------------------------
# О компании
# -----------------------------
@router.message(F.text == BTN_ABOUT)
async def about_company(message: Message):
    await message.answer(MSG_ABOUT_COMPANY, reply_markup=menu_for(message.from_user.id), parse_mode='HTML')


# -----------------------------
# ФОЛЛБЕК — работает только когда НЕТ состояний
# и НЕ трогает админку/сервисные команды ✅
# -----------------------------
@router.message(StateFilter(None))
async def fallback(message: Message):
    text_clean = (message.text or "").split(" (")[0]
    if text_clean in ALL_MENU_BUTTONS:
        return  # позволяем другим роутерам поймать

    await get_user(message.from_user.id, message.from_user)
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME_LOWER)
    services = "\n- ".join([
        BTN_HOROSCOPE, BTN_COMPATIBILITY, BTN_CANDIDATE_COMPATIBILITY, BTN_NUMEROLOGY, BTN_PHOTO_DESTINY,
        BTN_ZODIAC_QUIZ, BTN_LUCK_RESET, BTN_PAYMENT, BTN_ABOUT, BTN_SUBSCRIBE, BTN_PREMIUM
    ])

    user = await get_user(message.from_user.id, message.from_user)
    text = MSG_FALLBACK_GREETING.format(name=user_name, services=services)
    if not user.get("seen_disclaimer"):
        text += f"\n\n{DISCLAIMER}"
        user["seen_disclaimer"] = True
        await save_user(message.from_user.id, user)
    await message.answer(text, reply_markup=menu_for(message.from_user.id))
