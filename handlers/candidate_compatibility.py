from __future__ import annotations

from io import BytesIO
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from utils.constants import (
    BTN_CANDIDATE_COMPATIBILITY, BTN_CANCEL, BTN_DONE,
    MSG_NO_FREE_PAID, MSG_CANDIDATE_COMPATIBILITY_GREETING,
    MSG_CANDIDATE_REQUIRED_PROMPT, MSG_CANDIDATE_OPTIONAL_PROMPT,
    MSG_CANDIDATE_RESUME_PROMPT, MSG_CANDIDATE_COLLECTED,
    MSG_CANDIDATE_FILE_ERROR, DEFAULT_USER_NAME
)
from utils.button_matchers import is_candidate_compatibility_button
from utils.user_helpers import check_user_limit, get_user_name, get_user, save_user
from utils.message_helpers import format_response_with_balance
from utils.rate_limit import check_rate_limit
from utils.pricing_helpers import ensure_balance_and_charge, show_price_info
from keyboards.menus import menu_for, cancel_or_done_menu, cancel_menu
from utils.resume_ingest import extract_resume_text
from utils.resume_parser import parse_resume_text
from utils.candidate_compatibility import merge_candidate_profile, score_compatibility, build_humorous_response
from utils.company_params import get_company_params_text, parse_company_params

router = Router()


class CandidateCompatibilityStates(StatesGroup):
    waiting_required = State()
    waiting_optional = State()
    waiting_resume = State()


REQUIRED_FIELDS = [
    ("first_name", "имя"),
    ("last_name", "фамилию"),
    ("gender", "пол (м/ж/другое)"),
    ("age", "возраст"),
    ("experience_years", "опыт работы (лет)"),
]

OPTIONAL_FIELDS = [
    ("desired_role", "желаемую роль"),
    ("skills", "навыки (через запятую)"),
    ("education_level", "уровень образования"),
    ("work_format", "формат работы (удаленка/офис/гибрид)"),
    ("languages", "языки (через запятую)"),
    ("hobbies", "хобби (через запятую)"),
    ("email", "email"),
    ("phone", "телефон"),
    ("location", "локацию"),
]


@router.message(F.text.func(is_candidate_compatibility_button), StateFilter(None))
async def start_candidate_compatibility(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id, message.from_user)
    await show_price_info(message, user, "candidate_compatibility", "Совместимость с компанией")
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    await message.answer(MSG_CANDIDATE_COMPATIBILITY_GREETING.format(name=user_name), reply_markup=cancel_menu)
    await state.update_data(required_index=0, required={}, optional={}, resume_text=None)
    await state.set_state(CandidateCompatibilityStates.waiting_required)
    await message.answer(MSG_CANDIDATE_REQUIRED_PROMPT.format(field=REQUIRED_FIELDS[0][1]), reply_markup=cancel_menu)


@router.message(CandidateCompatibilityStates.waiting_required)
async def collect_required(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Меню открыто.", reply_markup=menu_for(message.from_user.id))
        return

    data = await state.get_data()
    idx = data.get("required_index", 0)
    field_key, _ = REQUIRED_FIELDS[idx]
    parsed = _parse_required_field(field_key, text)
    if parsed is None:
        await message.answer("Значение выглядит неверно. Попробуйте ещё раз.", reply_markup=cancel_menu)
        return

    required = data.get("required", {})
    required[field_key] = parsed
    idx += 1
    await state.update_data(required=required, required_index=idx)
    if idx >= len(REQUIRED_FIELDS):
        await state.set_state(CandidateCompatibilityStates.waiting_optional)
        await state.update_data(optional_index=0)
        await message.answer(MSG_CANDIDATE_OPTIONAL_PROMPT.format(field=OPTIONAL_FIELDS[0][1]), reply_markup=cancel_or_done_menu)
        return
    await message.answer(MSG_CANDIDATE_REQUIRED_PROMPT.format(field=REQUIRED_FIELDS[idx][1]), reply_markup=cancel_menu)


@router.message(CandidateCompatibilityStates.waiting_optional)
async def collect_optional(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Меню открыто.", reply_markup=menu_for(message.from_user.id))
        return
    if text.lower() == BTN_DONE.lower() or text.lower() == "готово":
        await state.set_state(CandidateCompatibilityStates.waiting_resume)
        await message.answer(MSG_CANDIDATE_RESUME_PROMPT, reply_markup=cancel_or_done_menu)
        return

    data = await state.get_data()
    idx = data.get("optional_index", 0)
    field_key, _ = OPTIONAL_FIELDS[idx]
    if text.lower() != "пропустить":
        optional = data.get("optional", {})
        optional[field_key] = _parse_optional_field(field_key, text)
        await state.update_data(optional=optional)

    idx += 1
    await state.update_data(optional_index=idx)
    if idx >= len(OPTIONAL_FIELDS):
        await state.set_state(CandidateCompatibilityStates.waiting_resume)
        await message.answer(MSG_CANDIDATE_RESUME_PROMPT, reply_markup=cancel_or_done_menu)
        return
    await message.answer(MSG_CANDIDATE_OPTIONAL_PROMPT.format(field=OPTIONAL_FIELDS[idx][1]), reply_markup=cancel_or_done_menu)


@router.message(CandidateCompatibilityStates.waiting_resume)
async def collect_resume(message: Message, state: FSMContext, bot: Bot):
    if message.text and message.text.strip().lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Меню открыто.", reply_markup=menu_for(message.from_user.id))
        return
    if message.text and message.text.strip().lower() in {BTN_DONE.lower(), "готово"}:
        await run_candidate_compatibility(message, state)
        return

    if not message.document:
        await message.answer("Пришлите файл резюме или нажмите «Готово».", reply_markup=cancel_or_done_menu)
        return

    buffer = BytesIO()
    try:
        await bot.download(message.document.file_id, destination=buffer)
    except Exception:
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, destination=buffer)
    buffer.seek(0)

    try:
        text = extract_resume_text(buffer.read(), message.document.file_name or "resume", message.document.mime_type or "")
    except Exception:
        await message.answer(MSG_CANDIDATE_FILE_ERROR, reply_markup=cancel_or_done_menu)
        return

    await state.update_data(resume_text=text)
    await run_candidate_compatibility(message, state)


async def run_candidate_compatibility(message: Message, state: FSMContext):
    user, has_limit = await check_user_limit(message.from_user.id, message.from_user)
    if not has_limit:
        await message.answer(MSG_NO_FREE_PAID, reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return

    allowed, wait_msg = check_rate_limit(user, "candidate_compatibility")
    if not allowed:
        await save_user(message.from_user.id, user)
        await message.answer(wait_msg, reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return

    charged = await ensure_balance_and_charge(
        message,
        "candidate_compatibility",
        user,
        "candidate_compatibility",
        {
            "required_fields": list(required.keys()),
            "optional_fields": list(optional.keys()),
            "has_resume": bool(resume_text),
            "resume_chars": len(resume_text or ""),
        }
    )
    if not charged:
        await state.clear()
        return
    user = charged

    await message.answer(MSG_CANDIDATE_COLLECTED, reply_markup=cancel_menu)

    data = await state.get_data()
    required = data.get("required", {})
    optional = data.get("optional", {})
    resume_text = data.get("resume_text")

    resume_data = parse_resume_text(resume_text) if resume_text else {}
    profile = merge_candidate_profile({**optional, **required}, resume_data)

    params_text = await get_company_params_text()
    company_params = parse_company_params(params_text)

    score, reasons = score_compatibility(profile, company_params)
    response = build_humorous_response(profile, score, reasons)

    await message.answer(
        format_response_with_balance(response, user),
        reply_markup=menu_for(message.from_user.id),
        parse_mode="HTML"
    )
    await state.clear()


def _parse_required_field(field_key: str, text: str):
    if not text:
        return None
    if field_key == "age":
        try:
            age = int(text)
            return age if age > 0 else None
        except ValueError:
            return None
    if field_key == "experience_years":
        try:
            return float(text.replace(",", "."))
        except ValueError:
            return None
    if field_key == "gender":
        lowered = text.lower()
        if lowered in {"м", "муж", "мужчина", "male"}:
            return "male"
        if lowered in {"ж", "жен", "женщина", "female"}:
            return "female"
        return "other"
    return text


def _parse_optional_field(field_key: str, text: str):
    if field_key in {"skills", "languages", "hobbies"}:
        return [item.strip() for item in text.split(",") if item.strip()]
    return text
