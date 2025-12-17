from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from datetime import datetime
from utils.constants import (
    BTN_SUBSCRIBE, BTN_UNSUBSCRIBE, BTN_CANCEL,
    MSG_SUBSCRIBE_ASK_BIRTHDATE, MSG_SUBSCRIBE_OK, MSG_UNSUB_OK,
    MSG_ALREADY_SUBSCRIBED, MSG_NOT_SUBSCRIBED, MSG_SUB_INVALID_DATE
)
from utils.user_helpers import get_user, save_user
from keyboards.menus import menu_for, cancel_menu

router = Router()


class SubscriptionStates(StatesGroup):
    waiting_birthdate = State()


def _unsubscribe_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_UNSUBSCRIBE)],
            [KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


@router.message(F.text == BTN_SUBSCRIBE, StateFilter(None))
async def start_subscribe(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id, message.from_user)
    sub = user.get("subscription") or {}

    if sub.get("active"):
        await state.clear()
        await message.answer(MSG_ALREADY_SUBSCRIBED, reply_markup=_unsubscribe_keyboard())
        return

    await message.answer(MSG_SUBSCRIBE_ASK_BIRTHDATE, reply_markup=cancel_menu)
    await state.set_state(SubscriptionStates.waiting_birthdate)


@router.message(F.text == BTN_UNSUBSCRIBE)
async def unsubscribe(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id, message.from_user)
    sub = user.get("subscription") or {}
    if not sub.get("active"):
        await message.answer(MSG_NOT_SUBSCRIBED, reply_markup=main_menu)
        await state.clear()
        return

    sub.update({"active": False, "last_sent": None})
    user["subscription"] = sub
    await save_user(message.from_user.id, user)
    await state.clear()
    await message.answer(MSG_UNSUB_OK, reply_markup=menu_for(message.from_user.id))


@router.message(SubscriptionStates.waiting_birthdate)
async def handle_birthdate(message: Message, state: FSMContext):
    if message.text.lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Возвращаю в меню.", reply_markup=menu_for(message.from_user.id))
        return

    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer(MSG_SUB_INVALID_DATE, reply_markup=cancel_menu)
        return

    user = await get_user(message.from_user.id, message.from_user)
    user["subscription"] = {
        "active": True,
        "birthdate": message.text.strip(),
        "time": "13:00",
        "last_sent": None,
    }
    await save_user(message.from_user.id, user)
    await state.clear()
    await message.answer(MSG_SUBSCRIBE_OK.format(time="13:00"), reply_markup=menu_for(message.from_user.id))
