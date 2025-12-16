from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_COMPATIBILITY, MSG_COMPATIBILITY_GREETING, MSG_INVALID_NAMES_FORMAT,
    MSG_NO_FREE_PAID, MSG_OLLAMA_COMPATIBILITY_ERROR, DEFAULT_USER_NAME
)
from utils.user_helpers import check_user_limit, decrement_user_limit, get_user_name, get_user
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from keyboards.menus import main_menu, payment_menu
from handlers.base import PaymentStates

router = Router()

class CompatibilityStates(StatesGroup):
    waiting_names = State()
    waiting_ollama_response = State()


@router.message(F.text == BTN_COMPATIBILITY, StateFilter(None))
async def start_compatibility(message: Message, state: FSMContext):
    await get_user(message.from_user.id, message.from_user)
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    await message.answer(MSG_COMPATIBILITY_GREETING.format(name=user_name))
    await state.set_state(CompatibilityStates.waiting_names)


@router.message(CompatibilityStates.waiting_names)
async def get_names(message: Message, state: FSMContext, bot: Bot):
    names = message.text.split(",")
    if len(names) != 2:
        await message.answer(MSG_INVALID_NAMES_FORMAT)
        return

    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        #await state.clear()
        await state.set_state(PaymentStates.choosing_amount)
        return

    await state.set_state(CompatibilityStates.waiting_ollama_response)

    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    name1, name2 = names[0].strip(), names[1].strip()
    
    prompt = (
        f"Ты магический бот-гадалка 🧙‍♂️✨. "
        f"Составь юмористический прогноз совместимости для имен: {name1} и {name2}. "
        f"Укажи уровень совместимости и советы по жизни. "
        f"Пользователь {user_name} имеет {user['free_count']} бесплатных и {user['paid_count']} платных обращений."
    )
    
    # Используем функцию с прогресс-баром
    from utils.ollama import ask_ollama
    response = await process_ollama_with_progress(
        bot, message.chat.id, ask_ollama, prompt
    )
    
    if not response.strip():
        response = MSG_OLLAMA_COMPATIBILITY_ERROR

    # Списание лимита
    user = await decrement_user_limit(
        message.from_user.id,
        feature="compatibility",
        details={"name1": name1, "name2": name2},
        telegram_user=message.from_user,
    )

    # Отправка ответа
    await message.answer(
        format_response_with_balance(response, user),
        reply_markup=main_menu, parse_mode='HTML'
    )
    await state.clear()
