"""
Утилиты для форматирования и отправки сообщений
"""

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from utils.constants import MSG_RESPONSE_WITH_BALANCE
from utils.user_helpers import format_balance
import asyncio
from aiogram.types import FSInputFile


async def send_typing_action(bot: Bot, chat_id: int) -> None:
    """
    Отправить индикатор набора текста
    
    Args:
        bot: Экземпляр бота
        chat_id: ID чата
    """
    try:
        await bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass


async def return_to_main_menu(
    message: Message,
    state: FSMContext,
    text: str = None,
    remove_keyboard: bool = False
) -> None:
    """
    Вернуть пользователя в главное меню
    
    Args:
        message: Сообщение от пользователя
        state: Состояние FSM
        text: Текст сообщения (если нужно, если None - используется стандартное сообщение)
        remove_keyboard: Удалить клавиатуру перед возвратом
    """
    from utils.constants import MSG_RETURNING_TO_MENU
    from keyboards.menus import menu_for
    from aiogram.types import ReplyKeyboardRemove
    
    await state.clear()
    
    reply_kb = menu_for(message.from_user.id)
    await message.answer(
        text or MSG_RETURNING_TO_MENU,
        reply_markup=reply_kb
    )


def format_response_with_balance(response: str, user: dict) -> str:
    """
    Форматировать ответ с балансом пользователя
    
    Args:
        response: Текст ответа
        user: Данные пользователя
        
    Returns:
        Отформатированное сообщение
    """
    balance = format_balance(user)
    return MSG_RESPONSE_WITH_BALANCE.format(response=response, balance=balance)


async def show_progress_bar(
        bot: Bot,
        chat_id: int,
        message_id: int,
        stop_event: asyncio.Event,
        total_steps: int = 40,
        step_delay: float = 2.2
) -> None:
    """
    Показать анимацию прогресс-бара с фиксированной шириной и иконкой "магического шара".

    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        message_id: ID сообщения для редактирования
        stop_event: Событие для остановки анимации
        total_steps: Количество шагов прогресс-бара
        step_delay: Задержка между шагами в секундах
    """
    try:
        bar_width = total_steps  # постоянная длина
        ball_emoji = "🔮"  # запасной вариант, если PNG не отобразится корректно

        while not stop_event.is_set():
            for i in range(1, total_steps + 1):
                if stop_event.is_set():
                    return

                progress = min(i * (100 // total_steps), 100)
                filled = i
                empty = bar_width - i

                # Формируем бар с фиксированной шириной
                bar = "[" + "█" * filled + " " * empty + f"] {progress}% {ball_emoji}"

                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=bar
                    )
                except Exception:
                    return

                await asyncio.sleep(step_delay)
                if stop_event.is_set():
                    return
    except Exception:
        pass


async def process_ollama_with_progress(
        bot: Bot,
        chat_id: int,
        ollama_call,
        *args,
        **kwargs
) -> str:
    """
    Выполнить запрос к Ollama с показом прогресс-бара и магическим шаром.

    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        ollama_call: Функция для вызова Ollama (async callable)
        *args: Аргументы для ollama_call
        **kwargs: Ключевые аргументы для ollama_call

    Returns:
        Ответ от Ollama
    """
    from utils.constants import MSG_QUERYING_UNIVERSE
    from pathlib import Path

    # Пути к ресурсам
    gif_path = Path("data/animated_magic_ball.gif")
    ball_path = Path("data/magic_ball.png")

    # Отправляем анимированный GIF
    try:
        gif_message = await bot.send_animation(
            chat_id=chat_id,
            animation=FSInputFile(gif_path),
            caption=MSG_QUERYING_UNIVERSE
        )
    except Exception:
        # fallback, если не удалось отправить gif
        gif_message = await bot.send_message(chat_id=chat_id, text=MSG_QUERYING_UNIVERSE)

    # Создаём событие для остановки прогресса
    stop_event = asyncio.Event()

    # Запускаем прогресс-бар поверх gif
    progress_msg = await bot.send_message(chat_id=chat_id, text="[                                ] 0% 🔮")
    progress_task = asyncio.create_task(
        show_progress_bar(bot, chat_id, progress_msg.message_id, stop_event)
    )

    try:
        response = await ollama_call(*args, **kwargs)
    finally:
        stop_event.set()
        await asyncio.sleep(0.2)
        progress_task.cancel()

        # Удаляем прогресс-бар и gif
        try:
            await bot.delete_message(chat_id=chat_id, message_id=progress_msg.message_id)
        except Exception:
            pass

        try:
            await bot.delete_message(chat_id=chat_id, message_id=gif_message.message_id)
        except Exception:
            pass

    return response
