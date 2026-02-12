from __future__ import annotations

import json

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
    MSG_CANDIDATE_EXPECT_FILE, MSG_CANDIDATE_PARSE_EMPTY, MSG_OLLAMA_CANDIDATE_ERROR,
    DEFAULT_USER_NAME
)
from utils.button_matchers import is_candidate_compatibility_button
from utils.user_helpers import check_user_limit, get_user_name, get_user, save_user
from utils.message_helpers import format_response_with_balance, process_ollama_with_progress
from utils.rate_limit import check_rate_limit
from utils.pricing_helpers import ensure_balance_and_charge, show_price_info
from keyboards.menus import menu_for, cancel_menu
from utils.resume_ingest import extract_resume_text
from utils.resume_parser import parse_resume_text
from utils.candidate_compatibility import (
    merge_candidate_profile,
    score_compatibility,
    build_humorous_response,
    get_mystic_insights,
)
from utils.company_params import get_company_params_text, parse_company_params
from utils.prompts import CANDIDATE_COMPATIBILITY_PROMPT, DISCLAIMER
from utils.ollama import ask_ollama

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
        await run_candidate_compatibility(
            message,
            state,
            bot,
            source="file",
            resume_file_id=message.document.file_id,
            resume_file_name=message.document.file_name or "resume",
            resume_file_mime=message.document.mime_type or "",
        )
        return

    if not message.text or not message.text.strip():
        await message.answer(MSG_CANDIDATE_EXPECT_FILE, reply_markup=cancel_menu)
        return
    text = message.text.strip()
    await run_candidate_compatibility(message, state, bot, source="text", resume_text=text)


async def run_candidate_compatibility(
    message: Message,
    state: FSMContext,
    bot: Bot,
    source: str,
    resume_text: str = "",
    resume_file_id: str = "",
    resume_file_name: str = "",
    resume_file_mime: str = "",
):
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

    await message.answer(MSG_CANDIDATE_COLLECTED, reply_markup=cancel_menu)

    async def _analyze_candidate_payload() -> dict:
        nonlocal resume_text
        if source == "file":
            if not resume_file_id:
                return {"error": "file_missing"}
            try:
                from io import BytesIO

                buffer = BytesIO()
                try:
                    await bot.download(resume_file_id, destination=buffer)
                except Exception:
                    file = await bot.get_file(resume_file_id)
                    await bot.download_file(file.file_path, destination=buffer)
                buffer.seek(0)
                resume_text = extract_resume_text(buffer.read(), resume_file_name, resume_file_mime)
            except Exception:
                return {"error": "file_parse"}

        parsed = parse_resume_text(resume_text) if resume_text else {}
        if not _has_core_candidate_fields(parsed):
            return {"error": "resume_empty", "resume_data": parsed, "resume_text": resume_text}

        params_text = await get_company_params_text()
        company_params = parse_company_params(params_text)
        mystic_profile = get_mystic_insights(parsed, company_params)
        prompt = CANDIDATE_COMPATIBILITY_PROMPT.format(
            company_params=params_text,
            parsed_profile=_profile_to_prompt_text(parsed),
            mystic_profile=_profile_to_prompt_text(mystic_profile.get("signals") or {}),
            resume_text=resume_text[:12000],
            disclaimer=DISCLAIMER,
        )
        ai_raw = await ask_ollama(prompt)
        if not _looks_like_ollama_error(ai_raw) and _needs_compatibility_expansion(ai_raw):
            refine_prompt = _build_refine_prompt(ai_raw, parsed, mystic_profile)
            refined = await ask_ollama(refine_prompt)
            if refined and not _looks_like_ollama_error(refined):
                ai_raw = refined
        return {
            "error": "",
            "resume_data": parsed,
            "resume_text": resume_text,
            "ai_response": ai_raw,
            "params_text": params_text,
        }

    analysis = await process_ollama_with_progress(
        bot,
        message.chat.id,
        _analyze_candidate_payload,
    )
    if not isinstance(analysis, dict):
        await message.answer(MSG_OLLAMA_CANDIDATE_ERROR, reply_markup=menu_for(message.from_user.id))
        await state.clear()
        return

    if analysis.get("error") == "file_parse":
        await message.answer(MSG_CANDIDATE_FILE_ERROR, reply_markup=cancel_menu)
        return
    if analysis.get("error") in {"resume_empty", "file_missing"}:
        await message.answer(MSG_CANDIDATE_PARSE_EMPTY, reply_markup=cancel_menu)
        return

    resume_data = analysis.get("resume_data") or {}
    resume_text = analysis.get("resume_text") or ""
    ai_response = (analysis.get("ai_response") or "").strip()
    params_text = analysis.get("params_text") or await get_company_params_text()

    charged = await ensure_balance_and_charge(
        message,
        "candidate_compatibility",
        user,
        "candidate_compatibility",
        {
            "source": source,
            "has_resume": bool(resume_text),
            "resume_chars": len(resume_text),
            "parsed_fields": sorted(list(resume_data.keys())),
        }
    )
    if not charged:
        await state.clear()
        return
    user = charged

    profile = merge_candidate_profile({}, resume_data)
    company_params = parse_company_params(params_text)
    mystic_insights = get_mystic_insights(profile, company_params)

    if ai_response and not _looks_like_ollama_error(ai_response):
        response = _enrich_ai_response(ai_response, profile, mystic_insights)
    else:
        score, reasons = score_compatibility(profile, company_params)
        response = build_humorous_response(profile, score, reasons, company_params)
        response = f"{response}\n\n{MSG_OLLAMA_CANDIDATE_ERROR}"

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


def _profile_to_prompt_text(profile: dict) -> str:
    if not profile:
        return "{}"
    try:
        return json.dumps(profile, ensure_ascii=False, indent=2)
    except Exception:
        return str(profile)


def _enrich_ai_response(ai_response: str, profile: dict, mystic_insights: dict) -> str:
    text = ai_response.strip()
    if not text:
        return text

    # Если LLM не вывел детали/мистику, добавляем компактную справку из парсера.
    has_details = "Детали:" in text or "Компании:" in text
    has_mystic = "Мистика:" in text or "Мистический слой" in text
    if has_details and has_mystic and len(text) >= 900:
        return text

    name = " ".join(x for x in [profile.get("first_name"), profile.get("last_name")] if x) or "не указано"
    age = profile.get("age")
    exp = profile.get("experience_years")
    location = profile.get("location") or "не указано"
    companies = profile.get("companies") or []
    skills = profile.get("skills") or []
    languages = profile.get("languages") or []

    parts = [text]
    if not has_details:
        tail = (
            "\n\nДетали:\n"
            f"- Имя: {name}\n"
            f"- Возраст: {age if age is not None else 'не указано'}\n"
            f"- Локация: {location}\n"
            f"- Опыт: {exp if exp is not None else 'не указано'}\n"
            f"- Компании: {', '.join(companies[:3]) if companies else 'не указано'}\n"
            f"- Навыки: {', '.join(skills[:6]) if skills else 'не указано'}\n"
            f"- Языки: {', '.join(languages[:4]) if languages else 'не указано'}"
        )
        parts.append(tail)

    if not has_mystic:
        mystic_lines = mystic_insights.get("details") or []
        mystic = "\n".join(mystic_lines[:8]) if mystic_lines else "- Звезды молчат, но мемы настроены дружелюбно."
        mystic_tail = f"\n\nМистика:\n{mystic}"
        parts.append(mystic_tail)

    return "".join(parts)


def _looks_like_ollama_error(text: str) -> bool:
    normalized = (text or "").strip().lower()
    if not normalized:
        return True
    error_markers = (
        "вселенная недоступна",
        "вселенная задумалась",
        "не смогла сгенерировать ответ",
        "попробуйте позже",
    )
    return any(marker in normalized for marker in error_markers)


def _needs_compatibility_expansion(text: str) -> bool:
    normalized = (text or "").strip().lower()
    if len(normalized) < 750:
        return True
    required = ("вердикт", "кандидат", "скор", "почему", "детали", "мистика")
    return any(key not in normalized for key in required)


def _build_refine_prompt(draft: str, parsed_profile: dict, mystic_profile: dict) -> str:
    return (
        "Перепиши и расширь черновик ответа ниже так, чтобы он был ярче, смешнее и мистичнее.\n"
        "Требования:\n"
        "1) Сохрани формат блоков: Вердикт / Кандидат / Скор / Почему / Детали / Мистика.\n"
        "2) Блок 'Мистика' сделай развернутым: астрология, нумерология, таро-расклад из 3 карт, "
        "китайский знак, лунная фаза, биоритмы.\n"
        "3) Юмор усили: каламбуры и офисная ирония, но без токсичности.\n"
        "4) Не придумывай факты, которых нет в профиле.\n"
        "5) Длина не менее 1200 символов.\n\n"
        f"Черновик:\n{draft}\n\n"
        f"Профиль:\n{_profile_to_prompt_text(parsed_profile)}\n\n"
        f"Мистические сигналы:\n{_profile_to_prompt_text(mystic_profile.get('signals') or {})}"
    )
