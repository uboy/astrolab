"""
Утилиты для форматирования и отправки сообщений
"""

from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from utils.constants import MSG_RESPONSE_WITH_BALANCE, MSG_QUERYING_UNIVERSE
from utils.user_helpers import format_balance
import asyncio


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
    from keyboards.menus import main_menu
    from aiogram.types import ReplyKeyboardRemove
    
    await state.clear()
    
    if remove_keyboard and text:
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.15)
    
    await message.answer(
        text or MSG_RETURNING_TO_MENU,
        reply_markup=main_menu
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
    total_steps: int = 20,
    step_delay: float = 1
) -> None:
    """
    Показать анимацию прогресс-бара (зацикленную)
    
    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        message_id: ID сообщения для редактирования
        stop_event: Событие для остановки анимации
        total_steps: Количество шагов прогресс-бара
        step_delay: Задержка между шагами в секундах
    """
    try:
        while not stop_event.is_set():
            for i in range(1, total_steps + 1):
                # Проверяем, не нужно ли остановить анимацию
                if stop_event.is_set():
                    return
                
                progress = min(i * (100 // total_steps), 100)
                filled = i
                empty = total_steps - i
                bar = "[" + "█" * filled + " " * empty + f"] {progress}%"
                
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=bar
                    )
                except Exception:
                    # Игнорируем ошибки редактирования (например, сообщение уже удалено)
                    return
                
                # Ждем перед следующим шагом
                await asyncio.sleep(step_delay)
                
                # Проверяем еще раз после задержки
                if stop_event.is_set():
                    return
    except Exception:
        # Игнорируем все ошибки в анимации
        pass


async def process_ollama_with_progress(
    bot: Bot,
    chat_id: int,
    ollama_call,
    *args,
    **kwargs
) -> str:
    """
    Выполнить запрос к Ollama с показом прогресс-бара
    
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
    
    # Отправляем сообщение о запросе во вселенную
    progress_msg = await bot.send_message(chat_id=chat_id, text=MSG_QUERYING_UNIVERSE)
    
    # Создаем событие для остановки анимации
    stop_event = asyncio.Event()
    
    # Запускаем анимацию прогресс-бара в фоне
    progress_task = asyncio.create_task(
        show_progress_bar(bot, chat_id, progress_msg.message_id, stop_event)
    )
    
    try:
        # Выполняем запрос к Ollama
        response = await ollama_call(*args, **kwargs)
    finally:
        # Останавливаем анимацию
        stop_event.set()
        # Даем время анимации завершиться
        try:
            await asyncio.sleep(0.2)
            progress_task.cancel()
        except Exception:
            pass
        
        # Удаляем сообщение с прогресс-баром
        try:
            await bot.delete_message(chat_id=chat_id, message_id=progress_msg.message_id)
        except Exception:
            # Игнорируем ошибки удаления (например, сообщение уже удалено)
            pass
    
    return response

