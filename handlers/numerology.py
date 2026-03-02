from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_NUMEROLOGY, BTN_YES, BTN_NO, BTN_CANCEL,
    MSG_NUMEROLOGY_GREETING, MSG_NUMEROLOGY_ASK_NAME, MSG_NUMEROLOGY_ASK_BIRTHDATE,
    MSG_INVALID_DATE_FORMAT, MSG_INVALID_NAME,
    MSG_UNDERAGE, MSG_OVERAGE, MSG_NO_FREE_PAID, MSG_OLLAMA_NUMEROLOGY_ERROR,
    DEFAULT_USER_NAME
)

from utils.user_helpers import check_user_limit, decrement_user_limit, get_user_name, get_user, save_user
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from keyboards.menus import menu_for, payment_menu, cancel_menu
from datetime import datetime, timezone
from handlers.base import PaymentStates
from utils.ollama import ask_ollama
from utils.rate_limit import check_rate_limit

router = Router()

CANCEL_WORDS = {"отмена", "назад", "в меню", "в главное меню", "/cancel", "/start"}

MONTH_NAMES = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
]


class NumerologyStates(StatesGroup):
    choosing_name_source = State()
    waiting_name = State()
    waiting_birthdate = State()
    waiting_ollama_response = State()


# ---------------------------------------------------------
# 🟦 Запуск нумерологии
# ---------------------------------------------------------
@router.message(F.text == BTN_NUMEROLOGY, StateFilter(None))
async def start_numerology(message: Message, state: FSMContext):
    await get_user(message.from_user.id, message.from_user)
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    profile_name = message.from_user.first_name or "не указано"

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_YES), KeyboardButton(text=BTN_NO)], [KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True
    )

    await message.answer(
        MSG_NUMEROLOGY_GREETING.format(name=user_name, profile_name=profile_name),
        reply_markup=keyboard
    )
    await state.set_state(NumerologyStates.choosing_name_source)


# ---------------------------------------------------------
# 🟥 ОТМЕНА из любого состояния
# ---------------------------------------------------------
@router.message(
    NumerologyStates.choosing_name_source,
    F.text.lower().in_(CANCEL_WORDS)
)
@router.message(
    NumerologyStates.waiting_name,
    F.text.lower().in_(CANCEL_WORDS)
)
@router.message(
    NumerologyStates.waiting_birthdate,
    F.text.lower().in_(CANCEL_WORDS)
)
async def cancel_numerology(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Хорошо, возвращаемся в главное меню 😊", reply_markup=menu_for(message.from_user.id))


# ---------------------------------------------------------
# 🟩 Пользователь выбирает использовать имя из профиля
# ---------------------------------------------------------
@router.message(NumerologyStates.choosing_name_source)
async def choose_name_source(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    profile_name = message.from_user.first_name or "не указано"

    if text in [BTN_YES.lower(), "yes", "да"]:
        # Используем имя из профиля
        user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
        await state.update_data(name=user_name)
        await state.set_state(NumerologyStates.waiting_birthdate)
        await message.answer(
            MSG_NUMEROLOGY_ASK_BIRTHDATE,
            reply_markup=ReplyKeyboardRemove()
        )
    elif text in [BTN_NO.lower(), "no", "нет"]:
        # Запрашиваем имя
        await state.set_state(NumerologyStates.waiting_name)
        await message.answer(
            MSG_NUMEROLOGY_ASK_NAME,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("⚠️ Пожалуйста, выберите 'Да' или 'Нет'. Использовать имя из профиля ({profile_name}) иначе можешь ввести своё?"
                             .format(profile_name=profile_name))


# ---------------------------------------------------------
# 🟦 Получаем пользовательское имя
# ---------------------------------------------------------
@router.message(NumerologyStates.waiting_name)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if not name or len(name) < 2:
        await message.answer(MSG_INVALID_NAME)
        return

    await state.update_data(name=name)
    await message.answer(MSG_NUMEROLOGY_ASK_BIRTHDATE)
    await state.set_state(NumerologyStates.waiting_birthdate)


# ---------------------------------------------------------
# 🟧 Получаем дату рождения
# ---------------------------------------------------------
@router.message(NumerologyStates.waiting_birthdate)
async def get_birthdate(message: Message, state: FSMContext, bot: Bot):
    # Парсим дату
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
    except ValueError:
        await message.answer(MSG_INVALID_DATE_FORMAT)
        return

    # Проверка возраста
    today = datetime.now(timezone.utc)
    age = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))

    if age < 18:
        await message.answer(MSG_UNDERAGE, reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return

    if age > 100:
        await message.answer(MSG_OVERAGE, reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return

    # Проверка лимита
    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        #await state.clear()
        await state.set_state(PaymentStates.choosing_amount)
        return
    allowed, wait_msg = check_rate_limit(user, "numerology")
    if not allowed:
        await save_user(message.from_user.id, user)
        await message.answer(wait_msg, reply_markup=main_menu)
        await state.clear()
        return

    await state.set_state(NumerologyStates.waiting_ollama_response)

    # Данные состояния
    data = await state.get_data()
    name = data.get("name", DEFAULT_USER_NAME)
    pretty_date = f"{dt.day} {MONTH_NAMES[dt.month - 1]} {dt.year}"

    prompt = (
        f"Ты магический бот-нумеролог 🧙‍♂️✨. "
        f"Проведи нумерологический анализ для {name}, родившегося {pretty_date}. "
        f"Используй нумерологию: рассчитай число судьбы, число имени, число жизненного пути. "
        f"Опиши характер, таланты, жизненные задачи, совместимость с числами, предсказания. "
        f"Добавь юмор, эмодзи, интересные факты. "
        f"У пользователя есть {user['free_count']} бесплатных и {user['paid_count']} платных обращений. "
        f"Используй забавный, дружелюбный и магический стиль с элементами нумерологии."
    )

    # Используем функцию с прогресс-баром
    from utils.ollama import ask_ollama
    response = await process_ollama_with_progress(
        bot, message.chat.id, ask_ollama, prompt
    )

    if not response.strip():
        response = MSG_OLLAMA_NUMEROLOGY_ERROR

    # Списание лимита
    user = await decrement_user_limit(
        message.from_user.id,
        feature="numerology",
        details={"name": name, "birthdate": message.text.strip(), "age": age},
        telegram_user=message.from_user,
    )

    # Отправка ответа
    await message.answer(
        format_response_with_balance(response, user),
        reply_markup=menu_for(message.from_user.id),
        parse_mode='HTML'
    )

    await state.clear()
