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
    score = 50
    reasons = []
    min_exp = company_params.get("min_experience_years")
    exp = profile.get("experience_years")
    if min_exp is not None and exp is not None:
        if float(exp) >= float(min_exp):
            score += 10
            reasons.append("Опыт соответствует ожиданиям")
        else:
            score -= 10
            reasons.append("Опыт ниже ожиданий")
    return max(0, min(100, score)), reasons


def build_humorous_response(profile: dict, score: int, reasons: list[str]) -> str:
    verdict = "Совместим ✅" if score >= 70 else "Скорее совместим 🤝" if score >= 50 else "Не совместим ❌"
    name = " ".join(x for x in [profile.get("first_name"), profile.get("last_name")] if x) or "Кандидат"
    summary = f"{name}, опыт: {profile.get('experience_years', 'не указан')}"
    reason_text = "; ".join(reasons) if reasons else "Магия сказала «давайте попробуем»"
    return f"Вердикт: {verdict}\nКандидат: {summary}\nПочему: {reason_text}"
