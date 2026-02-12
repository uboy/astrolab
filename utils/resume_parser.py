from __future__ import annotations

from datetime import datetime
import re

_EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
_PHONE_RE = re.compile(r"(\+?\d[\d\s\-\(\)]{8,}\d)")
_NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё'-]{1,}\s+[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё'-]{1,}$")
_NAME_STOP = {
    "resume", "резюме", "email", "skills", "top", "опыт", "experience", "summary",
    "profile", "contact", "contacts", "company", "компания", "position", "role",
}
_SKILL_SECTION_HEADERS = {"навыки", "skills", "top skills", "ключевые навыки"}
_SECTION_STOP_HEADERS = {
    "опыт", "experience", "образование", "education", "формат работы", "work format",
    "контакты", "contacts", "проекты", "projects", "языки", "languages",
}


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

    birthdate = _parse_birthdate(text)
    if birthdate:
        data["birthdate"] = birthdate

    exp_years = _parse_experience_years(text)
    if exp_years is not None:
        data["experience_years"] = exp_years

    age = _parse_age(text, birthdate)
    if age is not None:
        data["age"] = age

    gender = _parse_gender(text)
    if gender:
        data["gender"] = gender

    skills = _parse_skills(text, lines)
    if skills:
        data["skills"] = skills

    companies = _parse_companies(text, lines)
    if companies:
        data["companies"] = companies

    work_format = _parse_work_format(text)
    if work_format:
        data["work_format"] = work_format

    desired_role = _parse_labeled_text(text, ("позиция", "должность", "role", "position", "desired role"))
    if not desired_role:
        desired_role = _parse_role_from_lines(lines)
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
    for line in lines[:8]:
        normalized = _clean_line_token(line)
        if ":" in normalized:
            continue
        parts = normalized.split()
        if len(parts) != 2:
            continue
        if any(part.lower() in _NAME_STOP for part in parts):
            continue
        if _NAME_RE.match(normalized):
            return parts[0], parts[1]

    labeled = re.search(
        r"(?:имя|name)\s*:\s*([A-Za-zА-Яа-яЁё'-]{2,})\s+([A-Za-zА-Яа-яЁё'-]{2,})",
        text,
        re.IGNORECASE,
    )
    if labeled:
        return labeled.group(1), labeled.group(2)

    # Fallback for flattened PDF text where line structure is lost.
    tokenized = re.findall(r"\b([A-ZА-ЯЁ][a-zа-яё'-]{1,})\s+([A-ZА-ЯЁ][a-zа-яё'-]{1,})\b", text)
    for first, last in tokenized:
        first_l = first.lower()
        last_l = last.lower()
        if first_l in _NAME_STOP or last_l in _NAME_STOP:
            continue
        return first, last
    return None


def _parse_experience_years(text: str) -> float | None:
    # Explicit values: "4.5 года", "18+ years"
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*\+?\s*(?:год|года|лет|years?)", text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(",", "."))

    total_months = 0
    range_pattern = re.compile(
        r"(?<!\d)(\d{4})(?:[./-](\d{1,2}))?\s*[-–—]\s*(?:(\d{4})(?:[./-](\d{1,2}))?|present|current|now|н\.?\s*в\.?|по\s+н\.?\s*в\.?)",
        re.IGNORECASE,
    )
    now = datetime.utcnow()
    for match in range_pattern.finditer(text):
        start_year = int(match.group(1))
        start_month = _normalize_month(match.group(2))
        end_year_raw = match.group(3)
        if end_year_raw:
            end_year = int(end_year_raw)
            end_month = _normalize_month(match.group(4))
        else:
            end_year = now.year
            end_month = now.month
        months = (end_year - start_year) * 12 + (end_month - start_month)
        if months <= 0:
            continue
        total_months += months

    if total_months > 0:
        return round(total_months / 12.0, 1)

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


def _parse_age(text: str, birthdate: str | None = None) -> int | None:
    match = re.search(r"(?:возраст|age)\s*:\s*(\d{1,2})", text, re.IGNORECASE)
    if not match:
        match = re.search(r"\b(\d{1,2})\s*(?:лет|года|год|years?\s*old)\b", text, re.IGNORECASE)
    if match:
        value = int(match.group(1))
        if 14 <= value <= 90:
            return value

    if not birthdate:
        return None

    try:
        day, month, year = map(int, birthdate.split("."))
    except Exception:
        return None

    now = datetime.utcnow()
    age = now.year - year - ((now.month, now.day) < (month, day))
    if 14 <= age <= 90:
        return age
    return None


def _parse_birthdate(text: str) -> str | None:
    # 1) Надежный путь: явно подписанная дата рождения.
    labeled = re.finditer(
        r"(дата\s*рожд(?:ения)?|родил(?:ся|ась)|birth\s*date|date\s*of\s*birth|dob|born)\s*[:\-]?\s*([^\n|;,]+)",
        text,
        re.IGNORECASE,
    )
    for match in labeled:
        label = match.group(1).lower()
        value = match.group(2).strip()
        prefer_day_first = not any(token in label for token in ("birth", "dob", "born"))
        parsed = _parse_date_token(value, prefer_day_first=prefer_day_first)
        if parsed:
            return parsed

    # 2) Доп.путь: дата рядом с маркерами рождения.
    date_matches = re.finditer(r"(\d{1,2})[./-](\d{1,2})[./-](19\d{2}|20\d{2})", text)
    lowered = text.lower()
    for match in date_matches:
        start = max(0, match.start() - 28)
        end = min(len(text), match.end() + 28)
        context = lowered[start:end]
        if any(token in context for token in ("рожд", "birth", "dob", "born")):
            token = match.group(0)
            parsed = _parse_date_token(token, prefer_day_first=True)
            if parsed:
                return parsed

    return None


def _parse_date_token(token: str, prefer_day_first: bool) -> str | None:
    match = re.search(r"(\d{1,2})[./-](\d{1,2})[./-](19\d{2}|20\d{2})", token)
    if not match:
        return None
    a = int(match.group(1))
    b = int(match.group(2))
    year = int(match.group(3))

    # Однозначные случаи.
    if a > 12 and 1 <= b <= 12:
        day, month = a, b
    elif b > 12 and 1 <= a <= 12:
        day, month = b, a
    else:
        # Неоднозначные случаи: ориентируемся на язык маркера.
        if prefer_day_first:
            day, month = a, b
        else:
            month, day = a, b

    if not (1 <= day <= 31 and 1 <= month <= 12):
        return None
    return f"{day:02d}.{month:02d}.{year:04d}"


def _parse_gender(text: str) -> str | None:
    match = re.search(r"(?:пол|gender)\s*:\s*([^\n,.;|]+)", text, re.IGNORECASE)
    if match:
        value = match.group(1).strip().lower()
        return _normalize_gender(value)

    if re.search(r"\b(male|мужчина|муж)\b", text, re.IGNORECASE):
        return "male"
    if re.search(r"\b(female|женщина|жен)\b", text, re.IGNORECASE):
        return "female"
    return None


def _parse_skills(text: str, lines: list[str]) -> list[str]:
    for pattern in (
        r"(?:Навыки|Skills|Top Skills|Ключевые навыки)\s*:\s*([^\n]+)",
        r"(?:Навыки|Skills|Top Skills|Ключевые навыки)\s*\|\s*([^\n]+)",
    ):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parsed = _split_skill_items(match.group(1))
            if parsed:
                return parsed

    block = _extract_section_block(lines, headers=_SKILL_SECTION_HEADERS)
    if block:
        items: list[str] = []
        for line in block:
            cleaned = _clean_line_token(line)
            if not cleaned or ":" in cleaned:
                break
            parts = _split_skill_items(cleaned)
            if parts:
                items.extend(parts)
            elif _looks_like_skill(cleaned):
                items.append(cleaned)
        deduped = _dedupe(items)
        if deduped:
            return deduped[:12]

    return []


def _parse_companies(text: str, lines: list[str]) -> list[str]:
    companies: list[str] = []

    for match in re.finditer(r"(?:компания|company)\s*:\s*([^\n|]+)", text, re.IGNORECASE):
        value = _clean_company_name(match.group(1))
        if value:
            companies.append(value)

    for line in lines:
        if not re.search(r"\d{4}\s*[-–—]", line):
            continue
        for inner in re.findall(r"\(([^)]+)\)", line):
            value = _clean_company_name(inner)
            if value:
                companies.append(value)

    for line in lines:
        if re.search(r"\b(?:LLC|LTD|INC|CORP|GMBH|ООО|АО|ЗАО)\b", line, re.IGNORECASE):
            value = _clean_company_name(line)
            if value:
                companies.append(value)

    return _dedupe(companies)[:5]


def _parse_labeled_text(text: str, labels: tuple[str, ...]) -> str | None:
    label_pattern = "|".join(re.escape(x) for x in labels)
    match = re.search(rf"(?:{label_pattern})\s*:\s*([^\n|]+)", text, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip(" .;,-")
    return value or None


def _parse_languages(text: str) -> list[str]:
    value = _parse_labeled_text(text, ("языки", "languages"))
    if not value:
        return []
    parts = re.split(r"[,\|/;]", value)
    return _dedupe([p.strip() for p in parts if p.strip()])[:6]


def _extract_section_block(lines: list[str], headers: set[str]) -> list[str]:
    start = None
    for idx, line in enumerate(lines):
        normalized = _clean_line_token(line).lower()
        if normalized in headers:
            start = idx + 1
            break
    if start is None:
        return []

    block = []
    for line in lines[start:]:
        lowered = _clean_line_token(line).lower()
        if lowered in _SECTION_STOP_HEADERS:
            break
        if lowered.endswith(":") and lowered[:-1] in _SECTION_STOP_HEADERS:
            break
        block.append(line)
    return block


def _parse_work_format(text: str) -> str | None:
    match = re.search(r"(?:Формат работы|Work format)\s*:\s*([^\n|]+)", text, re.IGNORECASE)
    value = match.group(1).strip().lower() if match else text.lower()
    if "удален" in value or "remote" in value:
        return "remote"
    if "офис" in value or "office" in value:
        return "office"
    if "гибрид" in value or "hybrid" in value:
        return "hybrid"
    return None


def _parse_role_from_lines(lines: list[str]) -> str | None:
    role_keywords = (
        "developer", "engineer", "manager", "analyst", "architect", "lead",
        "разработ", "инженер", "менеджер", "аналитик", "архитектор", "тимлид",
    )
    for line in lines[:12]:
        normalized = _clean_line_token(line)
        lowered = normalized.lower()
        if ":" in normalized:
            continue
        if any(stop in lowered for stop in ("@", "email", "телефон", "phone", "опыт", "skills", "навыки")):
            continue
        if any(keyword in lowered for keyword in role_keywords):
            return normalized[:80]
    return None


def _normalize_month(raw: str | None) -> int:
    if not raw:
        return 1
    try:
        month = int(raw)
    except ValueError:
        return 1
    return min(12, max(1, month))


def _normalize_gender(value: str) -> str:
    if value in {"м", "муж", "мужчина", "male"}:
        return "male"
    if value in {"ж", "жен", "женщина", "female"}:
        return "female"
    return "other"


def _split_skill_items(raw: str) -> list[str]:
    chunks = re.split(r"[,|/;•]", raw)
    if len(chunks) == 1:
        chunks = raw.split()
    items = []
    for chunk in chunks:
        token = _clean_line_token(chunk)
        if not token:
            continue
        low = token.lower()
        if any(stop in low for stop in ("опыт", "experience", "summary", "резюме", "resume")):
            continue
        if len(token) > 35:
            continue
        items.append(token)
    return _dedupe(items)[:12]


def _clean_line_token(value: str) -> str:
    cleaned = value.strip().strip("•*-–— ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace("РЕЗЮМЕ", " ").replace("Resume", " ").strip()
    return cleaned


def _clean_company_name(value: str) -> str:
    cleaned = _clean_line_token(value)
    cleaned = re.sub(r"^(?:компания|company)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\d{4}\s*[-–—]\s*(?:\d{4}|present|current|now|н\.?\s*в\.?)", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip(" .;,-()")
    if not cleaned:
        return ""
    if len(cleaned.split()) > 8:
        return ""
    return cleaned


def _looks_like_skill(value: str) -> bool:
    low = value.lower()
    if any(char.isdigit() for char in value):
        return False
    if any(stop in low for stop in ("опыт", "experience", "образование", "education", "email", "телефон")):
        return False
    return 1 <= len(value.split()) <= 3


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result
