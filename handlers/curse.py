from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from utils.constants import (
    BTN_ZODIAC_QUIZ, BTN_CANCEL,
    MSG_ZODIAC_QUIZ_GREETING, MSG_ZODIAC_QUIZ_DONE, MSG_ZODIAC_QUIZ_ERROR,
    MSG_NO_FREE_PAID, DEFAULT_USER_NAME
)
from utils.user_helpers import check_user_limit, decrement_user_limit, get_user_name, save_user
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from keyboards.menus import menu_for, payment_menu
from handlers.base import PaymentStates
from utils.rate_limit import check_rate_limit
from utils.prompts import ZODIAC_QUIZ_PROMPT, DISCLAIMER

router = Router()

QUIZ_QUESTIONS = [
    {
        "question": "Вы скорее берёте инициативу или ждёте момента?",
        "options": ["Всегда впереди", "Жду подхода", "Смотря по настроению", "Доверяю судьбе", "Планирую до мелочей"]
    },
    {
        "question": "Как реагируете на конфликт?",
        "options": ["В лоб и сразу", "Переведу в шутку", "Ухожу в тишину", "Дипломатично", "Медленно, но верно убеждаю"]
    },
    {
        "question": "Любимая спонтанность?",
        "options": ["Внезапные поездки", "Ночные разговоры", "Эксперименты с едой", "Книги/кино под настроение", "Расписать всё до минуты"]
    },
    {
        "question": "Как отдыхаете после тяжёлого дня?",
        "options": ["Спорт/движение", "Тихий уют дома", "Встречи с друзьями", "Творчество", "Сон — лучший план"]
    },
    {
        "question": "Что вас мотивирует?",
        "options": ["Цель и победа", "Любопытство", "Стабильность", "Общение и поддержка", "Красота и комфорт"]
    },
    {
        "question": "Какой подарок выберете?",
        "options": ["Гаджет/инструмент", "Книга/курс", "Что-то для дома", "Сертификат на впечатления", "Что-то красивое и стильное"]
    },
]


class ZodiacQuizStates(StatesGroup):
    asking = State()


def _question_keyboard(options):
    rows = [[KeyboardButton(text=o)] for o in options]
    rows.append([KeyboardButton(text=BTN_CANCEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


@router.message(F.text == BTN_ZODIAC_QUIZ, StateFilter(None))
async def start_quiz(message: Message, state: FSMContext):
    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        await state.set_state(PaymentStates.choosing_amount)
        return

    await state.update_data(index=0, answers=[])
    await state.set_state(ZodiacQuizStates.asking)
    first_q = QUIZ_QUESTIONS[0]
    await message.answer(MSG_ZODIAC_QUIZ_GREETING)
    await message.answer(first_q["question"], reply_markup=_question_keyboard(first_q["options"]))


@router.message(ZodiacQuizStates.asking)
async def handle_quiz_answer(message: Message, state: FSMContext, bot: Bot):
    if (message.text or "").lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Возвращаю в меню.", reply_markup=menu_for(message.from_user.id))
        return

    data = await state.get_data()
    idx = data.get("index", 0)
    answers = data.get("answers", [])
    if idx >= len(QUIZ_QUESTIONS):
        idx = len(QUIZ_QUESTIONS) - 1

    current_q = QUIZ_QUESTIONS[idx]
    answers.append({"question": current_q["question"], "answer": message.text})
    idx += 1

    if idx < len(QUIZ_QUESTIONS):
        await state.update_data(index=idx, answers=answers)
        next_q = QUIZ_QUESTIONS[idx]
        await message.answer(next_q["question"], reply_markup=_question_keyboard(next_q["options"]))
        return

    # Собраны все ответы — просим ИИ угадать знак
    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=payment_menu)
        await state.set_state(PaymentStates.choosing_amount)
        return

    await message.answer(MSG_ZODIAC_QUIZ_DONE, reply_markup=_question_keyboard([]))

    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    answers_text = "\n".join([f"{a['question']} → {a['answer']}" for a in answers])
    prompt = ZODIAC_QUIZ_PROMPT.format(
        user_name=user_name,
        answers=answers_text,
        disclaimer=DISCLAIMER
    )

    from utils.ollama import ask_ollama
    allowed, wait_msg = check_rate_limit(user, "zodiac_quiz")
    if not allowed:
        await save_user(message.from_user.id, user)
        await message.answer(wait_msg, reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return
    response = await process_ollama_with_progress(
        bot, message.chat.id, ask_ollama, prompt
    )

    if not response.strip():
        response = MSG_ZODIAC_QUIZ_ERROR

    user = await decrement_user_limit(
        message.from_user.id,
        feature="zodiac_quiz",
        details={"answers": answers},
        telegram_user=message.from_user,
    )

    await message.answer(
        format_response_with_balance(response, user),
        reply_markup=menu_for(message.from_user.id),
        parse_mode='HTML'
    )
    await state.clear()
