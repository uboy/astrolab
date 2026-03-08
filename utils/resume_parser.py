from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
_PHONE_RE = re.compile(r"(\+?\d[\d\s\-\(\)]{8,}\d)")
_NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё'-]{1,}\s+[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё'-]{1,}$")


def parse_resume_text(text: str) -> dict:
    if not text or not text.strip():
        return {}

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    data: dict = {}

    name = _parse_name(lines, text)
    if name:
        data["first_name"], data["last_name"] = name

    email = _first_match(_EMAIL_RE, text)
    if email:
        data["email"] = email

    phone = _first_match(_PHONE_RE, text)
    if phone:
        data["phone"] = phone

    exp_years = _parse_experience_years(text)
    if exp_years is not None:
        data["experience_years"] = exp_years

    age = _parse_age(text)
    if age is not None:
        data["age"] = age

    gender = _parse_gender(text)
    if gender:
        data["gender"] = gender

    skills = _parse_skills(text, lines)
    if skills:
        data["skills"] = skills

    work_format = _parse_work_format(text)
    if work_format:
        data["work_format"] = work_format

    desired_role = _parse_labeled_text(text, ("позиция", "должность", "role", "position", "desired role"))
    if desired_role:
        data["desired_role"] = desired_role

    location = _parse_labeled_text(text, ("локация", "город", "location", "city"))
    if location:
        data["location"] = location

    education = _parse_labeled_text(text, ("образование", "education"))
    if education:
        data["education_level"] = education

    languages = _parse_languages(text)
    if languages:
        data["languages"] = languages

    return data


def _first_match(regex: re.Pattern, text: str) -> str | None:
    match = regex.search(text)
    return match.group(0) if match else None


def _parse_name(lines: list[str], text: str) -> tuple[str, str] | None:
    for line in lines[:5]:
        normalized = line.replace("РЕЗЮМЕ", "").replace("Resume", "").strip()
        if ":" in normalized:
            continue
        if _NAME_RE.match(normalized):
            parts = normalized.split()
            return parts[0], parts[1]

    labeled = re.search(r"(?:имя|name)\s*:\s*([A-Za-zА-Яа-яЁё'-]{2,})\s+([A-Za-zА-Яа-яЁё'-]{2,})", text, re.IGNORECASE)
    if labeled:
        return labeled.group(1), labeled.group(2)

    # Fallback for flattened PDF text where line structure is lost.
    tokenized = re.findall(r"\b([A-ZА-ЯЁ][a-zа-яё'-]{1,})\s+([A-ZА-ЯЁ][a-zа-яё'-]{1,})\b", text)
    stop = {"email", "skills", "опыт", "experience", "резюме", "resume"}
    for first, last in tokenized:
        if first.lower() in stop or last.lower() in stop:
            continue
        return first, last
    return None


def _parse_experience_years(text: str) -> float | None:
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:год|года|лет|years?)", text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(",", "."))

    ranges = re.findall(r"(\d{4})\s*[-–—]\s*(\d{4})", text)
    if ranges:
        total = 0
        for start, end in ranges:
            try:
                total += max(0, int(end) - int(start))
            except ValueError:
                continue
        if total > 0:
            return float(total)
    return None


def _parse_age(text: str) -> int | None:
    match = re.search(r"(?:возраст|age)\s*:\s*(\d{1,2})", text, re.IGNORECASE)
    if not match:
        match = re.search(r"\b(\d{1,2})\s*(?:лет|года|год|years?\s*old)\b", text, re.IGNORECASE)
    if not match:
        return None
    value = int(match.group(1))
    if 14 <= value <= 90:
        return value
    return None


def _parse_gender(text: str) -> str | None:
    match = re.search(r"(?:пол|gender)\s*:\s*([^\n,.;]+)", text, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip().lower()
    if value in {"м", "муж", "мужчина", "male"}:
        return "male"
    if value in {"ж", "жен", "женщина", "female"}:
        return "female"
    if value in {"other", "другое", "предпочитаю не указывать"}:
        return "other"
    return "other"


def _parse_skills(text: str, lines: list[str]) -> list[str]:
    skills = []
    match = re.search(r"(Навыки|Skills)\s*:\s*(.+)", text, re.IGNORECASE)
    if match:
        raw = match.group(2)
        parts = re.split(r"[,\|/]", raw)
        skills = [p.strip() for p in parts if p.strip()]
        return skills

    block = _extract_section_block(lines, headers={"навыки", "skills"})
    if block:
        raw = " ".join(block)
        parts = re.split(r"[,\|/]", raw)
        skills = [p.strip("•- \t") for p in parts if p.strip("•- \t")]
    return skills


def _parse_labeled_text(text: str, labels: tuple[str, ...]) -> str | None:
    label_pattern = "|".join(re.escape(x) for x in labels)
    match = re.search(rf"(?:{label_pattern})\s*:\s*([^\n]+)", text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()


def _parse_languages(text: str) -> list[str]:
    value = _parse_labeled_text(text, ("языки", "languages"))
    if not value:
        return []
    parts = re.split(r"[,\|/]", value)
    return [p.strip() for p in parts if p.strip()]


def _extract_section_block(lines: list[str], headers: set[str]) -> list[str]:
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() in headers:
            start = idx + 1
            break
    if start is None:
        return []
    stop_headers = {"опыт", "experience", "образование", "education", "формат работы", "work format"}
    block = []
    for line in lines[start:]:
        lowered = line.strip().lower()
        if lowered in stop_headers or lowered.endswith(":"):
            break
        block.append(line)
    return block


def _parse_work_format(text: str) -> str | None:
    match = re.search(r"Формат работы\s*:\s*(.+)", text, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip().lower()
    if "удален" in value:
        return "remote"
    if "офис" in value:
        return "office"
    if "гибрид" in value:
        return "hybrid"
    return value
