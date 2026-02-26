from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_PHOTO_DESTINY, MSG_PHOTO_DESTINY_GREETING, MSG_PHOTO_INVALID,
    MSG_NO_FREE_PAID, MSG_OLLAMA_PHOTO_ERROR, DEFAULT_USER_NAME, BTN_CANCEL
)
from utils.user_helpers import check_user_limit, decrement_user_limit, get_user_name, get_user
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from keyboards.menus import main_menu, payment_menu, cancel_menu
import base64
from handlers.base import PaymentStates

router = Router()

class PhotoDestinyStates(StatesGroup):
    waiting_photo = State()
    waiting_ollama_response = State()


@router.message(F.text == BTN_PHOTO_DESTINY, StateFilter(None))
async def start_photo_destiny(message: Message, state: FSMContext):
    await get_user(message.from_user.id, message.from_user)
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    await message.answer(
        MSG_PHOTO_DESTINY_GREETING.format(name=user_name),
        reply_markup=cancel_menu
    )
    await state.set_state(PhotoDestinyStates.waiting_photo)


@router.message(PhotoDestinyStates.waiting_photo, F.photo)
async def process_photo(message: Message, state: FSMContext, bot: Bot):
    # Проверяем лимиты перед обработкой
    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        #await state.clear()
        await state.set_state(PaymentStates.choosing_amount)
        return

    await state.set_state(PhotoDestinyStates.waiting_ollama_response)
    
    # Получаем фото (берем самое большое доступное)
    photo = message.photo[-1]
    
    try:
        # Скачиваем фото
        file_info = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file_info.file_path)
        
        # Читаем данные файла (file_data - это BytesIO объект)
        image_bytes = file_data.getvalue() if hasattr(file_data, 'getvalue') else file_data.read()
        
        # Если это BytesIO, закрываем его
        if hasattr(file_data, 'close'):
            file_data.close()
        
        # Конвертируем в base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
        
        prompt = (
            f"Ты магический бот-гадалка 🧙‍♂️✨. "
            f"Проанализируй это фото и определи судьбу человека на нём. "
            f"Опиши характер, жизненный путь, таланты, предсказания на будущее. "
            f"Используй физиогномику, анализ энергетики, магические знаки. "
            f"Добавь юмор, эмодзи, интересные наблюдения. "
            f"Пользователь {user_name} имеет {user['free_count']} бесплатных и {user['paid_count']} платных обращений. "
            f"Используй забавный, дружелюбный и магический стиль с элементами юмора."
        )
        
        # Используем функцию с прогресс-баром
        from utils.ollama import ask_ollama
        response = await process_ollama_with_progress(
            bot, message.chat.id, ask_ollama, prompt, images=[image_base64]
        )
        
        if not response.strip():
            response = MSG_OLLAMA_PHOTO_ERROR

        # Списание лимита
        user = await decrement_user_limit(
            message.from_user.id,
            feature="photo_destiny",
            details={"photo_file_id": photo.file_id},
            telegram_user=message.from_user,
        )

        # Отправка ответа
        await message.answer(
            format_response_with_balance(response, user),
            reply_markup=main_menu, parse_mode='HTML'
        )
        await state.clear()
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при обработке фото: {e}\nПопробуйте ещё раз.",
            reply_markup=main_menu
        )
        await state.clear()


@router.message(PhotoDestinyStates.waiting_photo, F.text == BTN_CANCEL)
async def cancel_photo(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Возвращаю в меню.", reply_markup=main_menu)


@router.message(PhotoDestinyStates.waiting_photo)
async def invalid_photo_input(message: Message, state: FSMContext):
    await message.answer(MSG_PHOTO_INVALID)
