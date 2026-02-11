from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
_PHONE_RE = re.compile(r"(\+?\d[\d\s\-\(\)]{8,}\d)")


def parse_resume_text(text: str) -> dict:
    if not text or not text.strip():
        return {}

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    data: dict = {}

    if lines:
        first = lines[0].replace("РЕЗЮМЕ", "").strip()
        if first:
            parts = first.split()
            if len(parts) >= 2:
                data["first_name"] = parts[0]
                data["last_name"] = parts[1]

    email = _first_match(_EMAIL_RE, text)
    if email:
        data["email"] = email

    phone = _first_match(_PHONE_RE, text)
    if phone:
        data["phone"] = phone

    exp_years = _parse_experience_years(text)
    if exp_years is not None:
        data["experience_years"] = exp_years

    skills = _parse_skills(text, lines)
    if skills:
        data["skills"] = skills

    work_format = _parse_work_format(text)
    if work_format:
        data["work_format"] = work_format

    return data


def _first_match(regex: re.Pattern, text: str) -> str | None:
    match = regex.search(text)
    return match.group(0) if match else None


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
