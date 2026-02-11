from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_COMPATIBILITY, MSG_COMPATIBILITY_GREETING, MSG_INVALID_NAMES_FORMAT,
    MSG_NO_FREE_PAID, MSG_OLLAMA_COMPATIBILITY_ERROR, DEFAULT_USER_NAME,
    BTN_DONE, BTN_CANCEL, MSG_COMPATIBILITY_PHOTO_PROMPT, MSG_COMPATIBILITY_COLLECTED
)
from utils.user_helpers import check_user_limit, get_user_name, get_user, save_user
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from keyboards.menus import menu_for, payment_menu, cancel_or_done_menu, cancel_menu
from handlers.base import PaymentStates
import base64
from io import BytesIO
from utils.rate_limit import check_rate_limit
from utils.prompts import COMPATIBILITY_PROMPT, DISCLAIMER
from utils.pricing_helpers import ensure_balance_and_charge, show_price_info

from utils.button_matchers import is_compatibility_button

router = Router()

MODE_TEXT = "Ввести имена и даты"
MODE_PHOTO = "Загрузить фото"


class CompatibilityStates(StatesGroup):
    choosing_mode = State()
    waiting_text = State()
    waiting_photos = State()
    waiting_ollama_response = State()


def _mode_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MODE_TEXT)],
            [KeyboardButton(text=MODE_PHOTO)],
            [KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


@router.message(F.text.func(is_compatibility_button), StateFilter(None))
async def start_compatibility(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id, message.from_user)
    await show_price_info(message, user, "compatibility", "Совместимость")
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    await message.answer(
        MSG_COMPATIBILITY_GREETING.format(name=user_name) + "\n\n" + MSG_COMPATIBILITY_PHOTO_PROMPT,
        reply_markup=cancel_menu
    )
    await state.set_state(CompatibilityStates.choosing_mode)
    await message.answer("Как собираем данные?", reply_markup=_mode_keyboard())


@router.message(CompatibilityStates.choosing_mode)
async def choose_mode(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Возвращаю в меню.", reply_markup=menu_for(message.from_user.id))
        return

    if text == MODE_TEXT:
        await state.set_state(CompatibilityStates.waiting_text)
        await message.answer(
            "Введите два имени и даты рождения через запятую или на разных строках.\nПример: Анна 12.05.1995, Денис 03.11.1992",
            reply_markup=cancel_menu
        )
        return

    if text == MODE_PHOTO:
        await state.update_data(photos=[], text_details=None)
        await state.set_state(CompatibilityStates.waiting_photos)
        await message.answer(
            "Пришлите два фото (можно с подписями). После второго запускаю анализ автоматически.",
            reply_markup=cancel_menu
        )
        return

    await message.answer("Выберите один из вариантов на клавиатуре.")


@router.message(CompatibilityStates.waiting_text)
async def get_text_details(message: Message, state: FSMContext, bot: Bot):
    if message.text.lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Меню открыто.", reply_markup=menu_for(message.from_user.id))
        return

    names = [x.strip() for x in message.text.replace("\n", ",").split(",") if x.strip()]
    if len(names) < 2:
        await message.answer(MSG_INVALID_NAMES_FORMAT)
        return

    await state.update_data(text_details=message.text.strip(), photos=[])
    await run_compatibility(message, state, bot)


async def _photo_to_base64(bot: Bot, file_id: str) -> str:
    buffer = BytesIO()
    try:
        await bot.download(file_id, destination=buffer)
    except Exception:
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, destination=buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


@router.message(CompatibilityStates.waiting_photos)
async def collect_photos(message: Message, state: FSMContext, bot: Bot):
    if message.text and message.text.lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Меню открыто.", reply_markup=menu_for(message.from_user.id))
        return

    data = await state.get_data()
    photos = data.get("photos", [])
    text_details = data.get("text_details")

    if message.photo:
        try:
            photo = message.photo[-1]
            photos.append(await _photo_to_base64(bot, photo.file_id))
            await state.update_data(photos=photos)
            await message.answer(f"Фото принято ({len(photos)}/2).", reply_markup=cancel_menu)
            if len(photos) >= 2:
                await run_compatibility(message, state, bot)
                return
        except Exception:
            await message.answer("Не удалось принять фото, попробуйте ещё раз или нажмите «Отмена».")
        return

    if message.text and not text_details:
        text_details = message.text.strip()
        await state.update_data(text_details=text_details)
        await message.answer("Записал подписи. Добавляйте фото.", reply_markup=cancel_menu)
        return

    await message.answer("Пришлите два фото.", reply_markup=cancel_menu)


async def run_compatibility(message: Message, state: FSMContext, bot: Bot):
    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        await state.set_state(PaymentStates.choosing_amount)
        return

    data = await state.get_data()
    text_details = data.get("text_details")
    photos = data.get("photos", [])
    allowed, wait_msg = check_rate_limit(user, "compatibility")
    if not allowed:
        await save_user(message.from_user.id, user)
        await message.answer(wait_msg, reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return

    charged = await ensure_balance_and_charge(
        message,
        "compatibility",
        user,
        "compatibility",
        {"text": text_details, "photos": len(photos)}
    )
    if not charged:
        await state.clear()
        return
    user = charged

    await state.set_state(CompatibilityStates.waiting_ollama_response)
    await message.answer(MSG_COMPATIBILITY_COLLECTED, reply_markup=cancel_menu)

    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    prompt = COMPATIBILITY_PROMPT.format(
        details=text_details or "Только фото",
        disclaimer=DISCLAIMER,
        user_name=user_name
    )

    from utils.ollama import ask_ollama
    response = await process_ollama_with_progress(
        bot, message.chat.id, ask_ollama, prompt, images=photos if photos else None
    )

    if not response.strip():
        response = MSG_OLLAMA_COMPATIBILITY_ERROR

    await message.answer(
        format_response_with_balance(response, user),
        reply_markup=menu_for(message.from_user.id), parse_mode='HTML'
    )
    await state.clear()
