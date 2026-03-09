from __future__ import annotations

import hashlib
import math
from datetime import datetime

from utils.zodiac import get_zodiac_sign

def merge_candidate_profile(user_input: dict, resume_data: dict) -> dict:
    merged = dict(resume_data or {})
    for key, value in (user_input or {}).items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        merged[key] = value
    return merged


def score_compatibility(profile: dict, company_params: dict):
    score = 45
    reasons = []
    min_exp = company_params.get("min_experience_years")
    exp = profile.get("experience_years")
    if min_exp is not None and exp is not None:
        if float(exp) >= float(min_exp):
            score += 20
            reasons.append("Опыт соответствует ожиданиям")
        else:
            score -= 15
            reasons.append("Опыт ниже ожиданий")
    elif exp is not None:
        score += 8
        reasons.append("Опыт кандидата удалось определить")

    preferred_work_format = company_params.get("preferred_work_format")
    candidate_work_format = profile.get("work_format")
    if preferred_work_format and candidate_work_format:
        if preferred_work_format == candidate_work_format:
            score += 12
            reasons.append("Формат работы совпадает с предпочтениями компании")
        else:
            score -= 8
            reasons.append("Формат работы отличается от предпочтений компании")

    skills = profile.get("skills") or []
    if skills:
        score += min(15, len(skills) * 3)
        reasons.append(f"В резюме найдено ключевых навыков: {len(skills)}")
    else:
        score -= 5
        reasons.append("Навыки в резюме почти не читаются")

    if profile.get("first_name") and profile.get("last_name"):
        score += 5
        reasons.append("Профиль кандидата заполнен достаточно подробно")

    if profile.get("desired_role"):
        score += 4
        reasons.append("Целевая роль кандидата определена")

    if profile.get("location"):
        score += 3
        reasons.append("Локация указана, логистика не в тумане")
        preferred_locations = company_params.get("preferred_locations") or []
        if preferred_locations:
            location = str(profile.get("location", "")).lower()
            matched = any(pref.lower() in location or location in pref.lower() for pref in preferred_locations)
            if matched:
                score += 5
                reasons.append("Локация совпадает с пожеланиями компании")
            else:
                reasons.append("Локация не совпала с приоритетной, но это решаемо")

    companies = profile.get("companies") or []
    if companies:
        score += min(8, len(companies) * 2)
        reasons.append(f"Опыт подтвержден компаниями: {len(companies)}")

    languages = profile.get("languages") or []
    if languages:
        score += min(6, len(languages) * 2)
        reasons.append(f"Языков в профиле: {len(languages)}")

    if profile.get("age") is not None:
        reasons.append("Возраст указан (для контекста, без дискриминации)")

    mystic = _compute_mystic_signals(profile, company_params or {})
    score += mystic.get("score_delta", 0)
    reasons.extend(mystic.get("reasons", []))

    return max(0, min(100, score)), reasons


def build_humorous_response(profile: dict, score: int, reasons: list[str], company_params: dict | None = None) -> str:
    verdict = "Совместим ✅" if score >= 70 else "Скорее совместим 🤝" if score >= 50 else "Не совместим ❌"
    summary = _build_candidate_summary(profile)
    reason_items = reasons[:5] if reasons else ["Магия сказала: «давайте попробуем»"]
    opener = (
        "Похоже, HR-кофемашина уже выставила режим «эспрессо одобрения»."
        if score >= 70
        else "Есть шанс, что команда не спрячется в переговорке после первого стендапа."
        if score >= 50
        else "Похоже, корпоративный мем-чат пока держит нейтралитет."
    )
    details = _build_details_block(profile, company_params or {})
    reasons_block = "\n".join(f"- {item}" for item in reason_items)
    return (
        f"{opener}\n"
        f"Вердикт: {verdict}\n"
        f"Кандидат: {summary}\n"
        f"Скор: {score}/100\n"
        f"Почему:\n{reasons_block}\n"
        f"Детали:\n{details}"
    )


def get_mystic_insights(profile: dict, company_params: dict | None = None) -> dict:
    return _compute_mystic_signals(profile, company_params or {})


def _build_candidate_summary(profile: dict) -> str:
    name = " ".join(x for x in [profile.get("first_name"), profile.get("last_name")] if x) or "Кандидат"
    parts = [name]

    age = profile.get("age")
    if age is not None:
        parts.append(f"возраст: {age}")
    else:
        parts.append("возраст: не указан")

    exp = profile.get("experience_years")
    if exp is not None:
        parts.append(f"опыт: {exp} лет")
    else:
        parts.append("опыт: не указан")

    desired_role = profile.get("desired_role")
    if desired_role:
        parts.append(f"роль: {desired_role}")

    work_format = profile.get("work_format")
    if work_format:
        parts.append(f"формат: {work_format}")

    skills = profile.get("skills") or []
    if skills:
        parts.append(f"навыки: {', '.join(skills[:5])}")

    location = profile.get("location")
    if location:
        parts.append(f"локация: {location}")

    return ", ".join(parts)


def _build_details_block(profile: dict, company_params: dict) -> str:
    lines = []

    companies = profile.get("companies") or []
    if companies:
        lines.append(f"- Компании: {', '.join(companies[:4])}")
    else:
        lines.append("- Компании: не удалось уверенно извлечь")

    languages = profile.get("languages") or []
    if languages:
        lines.append(f"- Языки: {', '.join(languages[:4])}")
    else:
        lines.append("- Языки: не указаны")

    work_format = profile.get("work_format")
    if work_format:
        lines.append(f"- Формат работы: {work_format}")
    else:
        lines.append("- Формат работы: не указан")

    role = profile.get("desired_role")
    if role:
        lines.append(f"- Роль: {role}")

    mystic = _compute_mystic_signals(profile, company_params)
    lines.append("- Мистический слой:")
    lines.extend(f"  {line}" for line in mystic.get("details", []))

    lines.append("- HR-юмор: если выдержал резюме-скан, выдержит и митинг в 9:59.")
    return "\n".join(lines)


def _compute_mystic_signals(profile: dict, company_params: dict) -> dict:
    score_delta = 0
    reasons = []
    details = []
    signals = {}

    birthdate = profile.get("birthdate")
    zodiac_name = "Неопределён"
    zodiac_emoji = "✨"
    candidate_element = None
    life_path = None

    if birthdate and isinstance(birthdate, str):
        try:
            day, month, year = map(int, birthdate.split("."))
            zodiac_name, zodiac_emoji = get_zodiac_sign(month, day)
            candidate_element = _zodiac_element(zodiac_name)
            planet = _zodiac_planet(zodiac_name)
            life_path = _life_path_number(day, month, year)
            chinese_sign = _chinese_zodiac(year)
            moon_phase = _birth_moon_phase(day, month, year)
            biorhythm = _biorhythm_snapshot(day, month, year)

            signals.update(
                {
                    "birthdate": birthdate,
                    "zodiac": f"{zodiac_emoji} {zodiac_name}",
                    "element": candidate_element,
                    "planet_ruler": planet,
                    "life_path_number": life_path,
                    "chinese_zodiac": chinese_sign,
                    "moon_phase": moon_phase,
                    "biorhythm": biorhythm,
                }
            )

            details.append(
                f"- Астрология: {zodiac_emoji} {zodiac_name}, стихия {candidate_element}, планета-покровитель {planet}."
            )
            details.append(
                f"- Нумерология: число судьбы {life_path}; китайский знак {chinese_sign}; лунная фаза '{moon_phase}'."
            )
            details.append(
                f"- Биоритмы: физика {biorhythm['physical']}%, эмоции {biorhythm['emotional']}%, интеллект {biorhythm['intellectual']}%."
            )
            reasons.append("Добавлен расширенный астрологический слой проверки")
        except Exception:
            details.append("- Звезды: дата рождения есть, но космос не разобрал формат.")
    else:
        details.append("- Звезды: дата рождения не указана, оракул ворчит.")

    full_name = " ".join(x for x in [profile.get("first_name"), profile.get("last_name")] if x).strip()
    name_number = _name_number(full_name)
    signals["name_number"] = name_number
    details.append(f"- Имя-вибрация: число имени {name_number} (да, бухгалтерия кармы ведется строго).")

    company_element = company_params.get("cosmic_element")
    if company_element and candidate_element:
        if company_element == candidate_element:
            score_delta += 5
            reasons.append("Стихия кандидата совпала с космопрофилем компании")
            details.append(f"- Стихийный матч: компания {company_element} + кандидат {candidate_element} = резонанс.")
        else:
            score_delta -= 2
            reasons.append("Стихии разные, но это не конец сказки")
            details.append(f"- Стихийный матч: компания {company_element}, кандидат {candidate_element}.")
    elif company_element:
        details.append(f"- Стихийный матч: у компании {company_element}, но кандидату не хватает даты рождения.")

    company_destiny = company_params.get("company_destiny_number")
    if company_destiny and life_path:
        distance = abs(int(company_destiny) - int(life_path))
        if distance == 0:
            score_delta += 4
            reasons.append("Числа судьбы совпали почти магически")
        elif distance == 1:
            score_delta += 2
            reasons.append("Числа судьбы близки, совместимость обещающая")
        else:
            score_delta -= 1
            reasons.append("Нумерология нейтральна, но шанс есть")
        details.append(f"- Матемагия: число компании {company_destiny}, кандидата {life_path}.")

    tarot_spread = _candidate_tarot_spread(profile)
    tarot_card = tarot_spread[0]
    signals["tarot_spread"] = tarot_spread
    details.append(f"- Таро-расклад: {tarot_spread[0]} / {tarot_spread[1]} / {tarot_spread[2]}.")
    details.append("- Пророчество офиса: если карты говорят 'Мир', то даже дедлайн начинает улыбаться.")

    company_tarot = company_params.get("company_tarot_card")
    if company_tarot:
        resonance = _card_resonance(company_tarot, tarot_spread)
        if resonance == "exact":
            score_delta += 3
            reasons.append("Таро-карты компании и кандидата в синхроне")
            details.append(f"- Таро-резонанс: компания и кандидат в точном аркане '{company_tarot}'.")
        elif resonance == "group":
            score_delta += 1
            reasons.append("Таро группы арканов совпали, мистический вайб положительный")
            details.append(f"- Таро-резонанс: арканы одной группы, компания '{company_tarot}'.")
        else:
            details.append(f"- Таро-резонанс: карта компании '{company_tarot}', кандидата '{tarot_card}'.")

    return {
        "score_delta": score_delta,
        "reasons": reasons,
        "details": details,
        "signals": signals,
    }


def _zodiac_element(zodiac_name: str) -> str:
    fire = {"Овен", "Лев", "Стрелец"}
    earth = {"Телец", "Дева", "Козерог"}
    air = {"Близнецы", "Весы", "Водолей"}
    water = {"Рак", "Скорпион", "Рыбы"}
    if zodiac_name in fire:
        return "fire"
    if zodiac_name in earth:
        return "earth"
    if zodiac_name in air:
        return "air"
    if zodiac_name in water:
        return "water"
    return "unknown"


def _life_path_number(day: int, month: int, year: int) -> int:
    digits = [int(ch) for ch in f"{day:02d}{month:02d}{year:04d}"]
    total = sum(digits)
    while total > 9:
        total = sum(int(ch) for ch in str(total))
    return total or 1


def _candidate_tarot_card(profile: dict) -> str:
    return _candidate_tarot_spread(profile)[0]


def _candidate_tarot_spread(profile: dict) -> list[str]:
    seed = (
        f"{profile.get('first_name','')}"
        f"{profile.get('last_name','')}"
        f"{profile.get('birthdate','')}"
        f"{profile.get('experience_years','')}"
    )
    cards = [
        "Маг", "Императрица", "Император", "Иерофант", "Влюбленные",
        "Колесница", "Сила", "Отшельник", "Колесо Фортуны", "Справедливость",
        "Повешенный", "Смерть", "Умеренность", "Дьявол", "Башня",
        "Звезда", "Луна", "Солнце", "Суд", "Мир",
    ]
    if not seed.strip():
        return ["Шут", "Звезда", "Мир"]
    base = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16)
    idx1 = base % len(cards)
    idx2 = (base // 7) % len(cards)
    idx3 = (base // 13) % len(cards)
    spread = [cards[idx1], cards[idx2], cards[idx3]]
    result = []
    for card in spread:
        if card not in result:
            result.append(card)
    while len(result) < 3:
        result.append(cards[(len(result) * 3) % len(cards)])
    return result[:3]


def _zodiac_planet(zodiac_name: str) -> str:
    mapping = {
        "Овен": "Марс",
        "Телец": "Венера",
        "Близнецы": "Меркурий",
        "Рак": "Луна",
        "Лев": "Солнце",
        "Дева": "Меркурий",
        "Весы": "Венера",
        "Скорпион": "Плутон",
        "Стрелец": "Юпитер",
        "Козерог": "Сатурн",
        "Водолей": "Уран",
        "Рыбы": "Нептун",
    }
    return mapping.get(zodiac_name, "Хирон")


def _chinese_zodiac(year: int) -> str:
    animals = [
        "Крыса", "Бык", "Тигр", "Кролик", "Дракон", "Змея",
        "Лошадь", "Коза", "Обезьяна", "Петух", "Собака", "Свинья",
    ]
    return animals[(year - 1900) % 12]


def _birth_moon_phase(day: int, month: int, year: int) -> str:
    # Упрощенная оценка: достаточно для развлекательного контента.
    dt = datetime(year, month, day)
    known_new_moon = datetime(2000, 1, 6)
    synodic = 29.530588853
    days = (dt - known_new_moon).days % synodic
    phases = [
        (1.85, "Новолуние"),
        (5.54, "Растущий серп"),
        (9.23, "Первая четверть"),
        (12.92, "Растущая луна"),
        (16.61, "Полнолуние"),
        (20.30, "Убывающая луна"),
        (23.99, "Последняя четверть"),
        (27.68, "Стареющий серп"),
    ]
    for threshold, label in phases:
        if days < threshold:
            return label
    return "Новолуние"


def _biorhythm_snapshot(day: int, month: int, year: int) -> dict:
    born = datetime(year, month, day)
    now = datetime.utcnow()
    days_alive = max(1, (now - born).days)
    return {
        "physical": int(math.sin(2 * math.pi * days_alive / 23) * 100),
        "emotional": int(math.sin(2 * math.pi * days_alive / 28) * 100),
        "intellectual": int(math.sin(2 * math.pi * days_alive / 33) * 100),
    }


def _name_number(name: str) -> int:
    if not name:
        return 0
    cleaned = "".join(ch for ch in name.lower() if ch.isalpha())
    if not cleaned:
        return 0
    total = sum(ord(ch) for ch in cleaned)
    while total > 9:
        total = sum(int(ch) for ch in str(total))
    return total


def _card_resonance(company_card: str, spread: list[str]) -> str:
    normalized_company = _normalize_card(company_card)
    normalized_spread = [_normalize_card(x) for x in spread]
    if normalized_company in normalized_spread:
        return "exact"
    major_light = {"солнце", "звезда", "мир", "суд", "умеренность"}
    major_hard = {"башня", "дьявол", "смерть", "повешенный"}
    if normalized_company in major_light and any(card in major_light for card in normalized_spread):
        return "group"
    if normalized_company in major_hard and any(card in major_hard for card in normalized_spread):
        return "group"
    return "none"


def _normalize_card(value: str) -> str:
    return (value or "").strip().lower().replace("ё", "е")
