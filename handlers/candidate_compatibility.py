from __future__ import annotations

from io import BytesIO
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from utils.constants import (
    BTN_CANDIDATE_COMPATIBILITY, BTN_CANCEL,
    MSG_NO_FREE_PAID, MSG_CANDIDATE_COMPATIBILITY_GREETING,
    MSG_CANDIDATE_TEXT_RESUME_GUIDE, MSG_CANDIDATE_TEXT_RESUME_PROMPT,
    MSG_CANDIDATE_RESUME_PROMPT, MSG_CANDIDATE_COLLECTED, MSG_CANDIDATE_FILE_ERROR,
    MSG_CANDIDATE_EXPECT_FILE, MSG_CANDIDATE_PARSE_EMPTY,
    DEFAULT_USER_NAME
)
from utils.button_matchers import is_candidate_compatibility_button
from utils.user_helpers import check_user_limit, get_user_name, get_user, save_user
from utils.message_helpers import format_response_with_balance
from utils.rate_limit import check_rate_limit
from utils.pricing_helpers import ensure_balance_and_charge, show_price_info
from keyboards.menus import menu_for, cancel_menu
from utils.resume_ingest import extract_resume_text
from utils.resume_parser import parse_resume_text
from utils.candidate_compatibility import merge_candidate_profile, score_compatibility, build_humorous_response
from utils.company_params import get_company_params_text, parse_company_params

router = Router()


class CandidateCompatibilityStates(StatesGroup):
    waiting_resume = State()


@router.message(F.text.func(is_candidate_compatibility_button), StateFilter(None))
async def start_candidate_compatibility(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id, message.from_user)
    await show_price_info(message, user, "candidate_compatibility", "Совместимость с компанией")
    user_name = get_user_name(message.from_user.first_name, DEFAULT_USER_NAME)
    await message.answer(MSG_CANDIDATE_COMPATIBILITY_GREETING.format(name=user_name), reply_markup=cancel_menu)
    await state.set_state(CandidateCompatibilityStates.waiting_resume)
    await message.answer(MSG_CANDIDATE_RESUME_PROMPT, reply_markup=cancel_menu)
    await message.answer(MSG_CANDIDATE_TEXT_RESUME_GUIDE, reply_markup=cancel_menu)
    await message.answer(MSG_CANDIDATE_TEXT_RESUME_PROMPT, reply_markup=cancel_menu)


@router.message(CandidateCompatibilityStates.waiting_resume)
async def collect_resume(message: Message, state: FSMContext, bot: Bot):
    if message.text and message.text.strip().lower() == BTN_CANCEL.lower():
        await state.clear()
        await message.answer("Отменено. Меню открыто.", reply_markup=menu_for(message.from_user.id))
        return

    if message.document:
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
            await message.answer(MSG_CANDIDATE_FILE_ERROR, reply_markup=cancel_menu)
            return

        await run_candidate_compatibility(message, state, resume_text=text, source="file")
        return

    if not message.text or not message.text.strip():
        await message.answer(MSG_CANDIDATE_EXPECT_FILE, reply_markup=cancel_menu)
        return
    text = message.text.strip()
    await run_candidate_compatibility(message, state, resume_text=text, source="text")


async def run_candidate_compatibility(message: Message, state: FSMContext, resume_text: str, source: str):
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

    resume_data = parse_resume_text(resume_text) if resume_text else {}
    if not _has_core_candidate_fields(resume_data):
        await message.answer(MSG_CANDIDATE_PARSE_EMPTY, reply_markup=cancel_menu)
        return

    charged = await ensure_balance_and_charge(
        message,
        "candidate_compatibility",
        user,
        "candidate_compatibility",
        {
            "source": source,
            "has_resume": bool(resume_text),
            "resume_chars": len(resume_text or ""),
            "parsed_fields": sorted(list(resume_data.keys())),
        }
    )
    if not charged:
        await state.clear()
        return
    user = charged

    await message.answer(MSG_CANDIDATE_COLLECTED, reply_markup=cancel_menu)

    profile = merge_candidate_profile({}, resume_data)

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


def _has_core_candidate_fields(data: dict) -> bool:
    if not data:
        return False
    has_name = bool(data.get("first_name") and data.get("last_name"))
    has_exp = data.get("experience_years") is not None
    has_skills = bool(data.get("skills"))
    return has_name or has_exp or has_skills
