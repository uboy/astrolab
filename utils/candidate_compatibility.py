from __future__ import annotations


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

    return max(0, min(100, score)), reasons


def build_humorous_response(profile: dict, score: int, reasons: list[str]) -> str:
    verdict = "Совместим ✅" if score >= 70 else "Скорее совместим 🤝" if score >= 50 else "Не совместим ❌"
    summary = _build_candidate_summary(profile)
    reason_text = "; ".join(reasons) if reasons else "Магия сказала «давайте попробуем»"
    return f"Вердикт: {verdict}\nКандидат: {summary}\nСкор: {score}/100\nПочему: {reason_text}"


def _build_candidate_summary(profile: dict) -> str:
    name = " ".join(x for x in [profile.get("first_name"), profile.get("last_name")] if x) or "Кандидат"
    parts = [name]

    age = profile.get("age")
    if age is not None:
        parts.append(f"{age} лет")

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
