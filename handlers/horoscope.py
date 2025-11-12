from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.ollama import ask_ollama
from utils.constants import (
    BTN_HOROSCOPE, MSG_HOROSCOPE_GREETING, MSG_INVALID_DATE_FORMAT,
    MSG_UNDERAGE, MSG_OVERAGE, MSG_NO_FREE_PAID, MSG_OLLAMA_HOROSCOPE_ERROR,
    DEFAULT_USER_NAME, MSG_BALANCE_FORMAT
)
from utils.user_helpers import check_user_limit, decrement_user_limit, get_user_name
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from keyboards.menus import main_menu, payment_menu
from datetime import datetime, timezone

router = Router()

MONTH_NAMES = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
]

class HoroscopeStates(StatesGroup):
    waiting_birthdate = State()
    waiting_ollama_response = State()


@router.message(F.text == BTN_HOROSCOPE, StateFilter(None))
async def start_horoscope(message: Message, state: FSMContext):
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    await message.answer(
        MSG_HOROSCOPE_GREETING.format(name=user_name),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(HoroscopeStates.waiting_birthdate)


@router.message(HoroscopeStates.waiting_birthdate)
async def get_birthdate(message: Message, state: FSMContext, bot: Bot):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
    except ValueError:
        await message.answer(MSG_INVALID_DATE_FORMAT)
        return

    # Проверка возраста
    today = datetime.now(timezone.utc)
    age = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
    
    if age < 18:
        await message.answer(MSG_UNDERAGE, reply_markup=main_menu)
        await state.clear()
        return
    
    if age > 100:
        await message.answer(MSG_OVERAGE, reply_markup=main_menu)
        await state.clear()
        return

    user, has_limit = await check_user_limit(message.from_user.id)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        await state.clear()
        return

    await state.set_state(HoroscopeStates.waiting_ollama_response)

    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    pretty_date = f"{dt.day} {MONTH_NAMES[dt.month - 1]} {dt.year}"
    
    prompt = (
        f"Ты магический бот-гадалка 🧙‍♂️✨. "
        f"Составь весёлый гороскоп для {user_name}, родившегося {pretty_date}. "
        f"Добавь юмор, эмодзи, советы по жизни, краткий прогноз, "
        f"укажи, сколько у пользователя есть {user['free_count']} бесплатных и {user['paid_count']} платных обращений. "
        f"Используй забавный, дружелюбный и магический стиль."
    )
    
    # Используем функцию с прогресс-баром
    from utils.ollama import ask_ollama
    response = await process_ollama_with_progress(
        bot, message.chat.id, ask_ollama, prompt
    )
    
    if not response.strip():
        response = MSG_OLLAMA_HOROSCOPE_ERROR

    # Списание лимита
    user = await decrement_user_limit(message.from_user.id)

    # Отправка ответа
    await message.answer(
        format_response_with_balance(response, user),
        reply_markup=main_menu
    )
    await state.clear()
