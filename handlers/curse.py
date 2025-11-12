#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiogram import Router, F, Bot
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_CURSE_REMOVAL, BTN_BACK, MSG_CURSE_REMOVAL_START,
    MSG_NO_FREE_PAID, MSG_OLLAMA_CURSE_ERROR, MSG_RETURNED_TO_MENU,
    DEFAULT_USER_NAME
)
from utils.user_helpers import check_user_limit, decrement_user_limit, get_user_name
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from keyboards.menus import main_menu, payment_menu
from handlers.base import PaymentStates

router = Router()

class CurseStates(StatesGroup):
    choosing_curse = State()
    waiting_ollama_response = State()

# -----------------------------
# Список готовых порч
# -----------------------------
CURSES = [
    {"title": "Общая/жизненная порча", "phrase": "Чувствую тяжесть и усталость, всё валится из рук — снимите порчу."},
    {"title": "Семейная/социальная порча", "phrase": "В доме конфликты, злость кипит — кто-то навёл злые глаза."},
    {"title": "Порча на бедность/растрату", "phrase": "Деньги уходят сквозь пальцы, нечего держать — заговор на нищету."},
    {"title": "Порча на работу/успех", "phrase": "С работой не везёт: увольнения, проекты рушатся — порча на карьеру."},
    {"title": "Порча на отношения/любовную разлуку", "phrase": "Счастье в семье ушло: муж охладел, измены, отречение детей."},
    {"title": "Порча на детей", "phrase": "Дети болеют, неуспевают, тянет в плохое — порча на детей."},
    {"title": "Порча на здоровье", "phrase": "Здоровье рушится inexplicably — врачи не находят причину."},
    {"title": "Порча на сон/кошмары", "phrase": "Сон словно разорван: кошмары, бессонница, дурные сны."},
    {"title": "Порча на плодородие", "phrase": "Я не могу забеременеть/роды осложняются — порча на плод."},
    {"title": "Порча на психику/депрессия", "phrase": "Постоянный страх, беспокойство, депрессия — будто душу затянули."},
    {"title": "Порча на удачу", "phrase": "Враг всюду: вещи теряются, планы ломают, люди отвернулись."},
    {"title": "Магическое преследование", "phrase": "Чувствую, что за мной следят - дурные видения и предзнаменования."},
    {"title": "Деловая/контрактная порча", "phrase": "Кошель идёт на убыль, налоги/штрафы бешеные — кто-то уроняет мой достаток."},
    {"title": "Порча на дом/пространство", "phrase": "Дом пустой от гостей, растения чахнут — порча на дом."},
    {"title": "Обрядовая/артефакт-порча", "phrase": "Чёрные знаки: опухоли, ругательства, найденные куклы/иглы."},
    {"title": "Порча на репутацию", "phrase": "Меня оболгали, репутация рушится — порча на честь и имя."},
    {"title": "Подселение/внедрение", "phrase": "Чувствую чужую энергию в себе — не своё поведение, мысли."},
    {"title": "Порча на технику/транспорт", "phrase": "Постоянные аварии, поломки — порча на технику и транспорт."},
    {"title": "Привязка/энергетическая связь", "phrase": "Нельзя щелкнуть пальцами: всё идёт на перекосяк после определённого человека."},
    {"title": "Диагностика/неизвестная порча", "phrase": "Хочу проверить — есть ли порча и кто наводил."},
]


# -----------------------------
# Старт снятия порчи
# -----------------------------
@router.message(F.text == BTN_CURSE_REMOVAL, StateFilter(None))
async def start_curse(message: Message, state: FSMContext):
    # Создаем кнопки в 2 колонки
    keyboard_rows = []
    for i in range(0, len(CURSES), 2):
        row = [KeyboardButton(text=CURSES[i]["title"])]
        if i + 1 < len(CURSES):
            row.append(KeyboardButton(text=CURSES[i + 1]["title"]))
        keyboard_rows.append(row)
    # Добавляем кнопку "Назад" в отдельную строку
    keyboard_rows.append([KeyboardButton(text=BTN_BACK)])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )
    await state.set_state(CurseStates.choosing_curse)
    await message.answer(MSG_CURSE_REMOVAL_START, reply_markup=keyboard)


# -----------------------------
# Выбор готовой порчи или пользовательский текст
# -----------------------------
@router.message(CurseStates.choosing_curse)
async def choose_curse(message: Message, state: FSMContext, bot: Bot):
    text = message.text.strip()
    if text.lower() == BTN_BACK.lower():
        await state.clear()
        await message.answer(MSG_RETURNED_TO_MENU, reply_markup=main_menu)
        return

    # Проверяем, есть ли совпадение с готовыми порчами
    selected = next((c for c in CURSES if c["title"].lower() == text.lower()), None)
    if selected:
        curse_text = selected["phrase"]
    else:
        # Пользовательский текст
        curse_text = text

    await state.update_data(curse_phrase=curse_text)
    await state.set_state(CurseStates.waiting_ollama_response)
    await process_ollama_curse(message, state, bot)


# -----------------------------
# Обработка запроса к Ollama
# -----------------------------
async def process_ollama_curse(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    curse_text = data.get("curse_phrase", "")
    user, has_limit = await check_user_limit(message.from_user.id)

    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        #await state.clear()
        await state.set_state(PaymentStates.choosing_amount)
        return

    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    prompt = (
        f"Ты магический бот-гадалка 🧙‍♂️✨. "
        f"Сними порчу для {user_name}, используя вариант: {curse_text}. "
        f"У пользователя есть {user['free_count']} бесплатных и {user['paid_count']} платных обращений. "
        f"Дай пошаговые рекомендации в магическом и дружелюбном стиле."
    )

    # Используем функцию с прогресс-баром
    from utils.ollama import ask_ollama
    response = await process_ollama_with_progress(
        bot, message.chat.id, ask_ollama, prompt
    )
    
    if not response.strip():
        response = MSG_OLLAMA_CURSE_ERROR

    # Списание лимита
    user = await decrement_user_limit(message.from_user.id)

    # Отправка ответа
    await message.answer(
        format_response_with_balance(response, user),
        reply_markup=main_menu, parse_mode='HTML'
    )
    await state.clear()
