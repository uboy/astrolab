from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from utils.constants import BTN_ADMIN_PRICES, MSG_NO_ACCESS
from utils.prices import get_prices, set_price
from utils.config import settings

router = Router()

class PriceStates(StatesGroup):
    waiting_price = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMINS


@router.message(F.text == BTN_ADMIN_PRICES, StateFilter(None))
async def prices_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return
    prices = await get_prices()
    text_lines = [f"{k}: {v}" for k, v in prices.items()]
    await state.set_state(PriceStates.waiting_price)
    await message.answer("Текущие цены:\n" + "\n".join(text_lines) + "\nВведите: название цена (например, horoscope 2)")


@router.message(PriceStates.waiting_price)
async def prices_set(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(MSG_NO_ACCESS)
        return
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("Используйте формат: название цена (например, horoscope 2)")
        return
    feature, value = parts
    try:
        val = int(value)
    except ValueError:
        await message.answer("Цена должна быть числом.")
        return
    await set_price(feature, val)
    prices = await get_prices()
    text_lines = [f"{k}: {v}" for k, v in prices.items()]
    await message.answer("Цены обновлены:\n" + "\n".join(text_lines))
    await state.clear()
