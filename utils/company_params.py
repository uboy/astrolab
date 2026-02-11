from __future__ import annotations

import re
from utils.json_db import read_json, write_json
from utils.constants import DEFAULT_COMPANY_PARAMS_TEXT

PARAMS_FILE = "data/company_params.json"


async def get_company_params_text() -> str:
    data = await read_json(PARAMS_FILE)
    if not isinstance(data, dict):
        data = {}
    text = data.get("text")
    if not text:
        text = DEFAULT_COMPANY_PARAMS_TEXT
        await write_json(PARAMS_FILE, {"text": text})
    return text


async def set_company_params_text(text: str) -> None:
    await write_json(PARAMS_FILE, {"text": text})


def parse_company_params(text: str) -> dict:
    lowered = text.lower()
    params = {}

    match = re.search(r"(?:опыт|experience)\s*[:\-]?\s*(\d+(?:[.,]\d+)?)", lowered)
    if match:
        params["min_experience_years"] = float(match.group(1).replace(",", "."))

    if "удален" in lowered:
        params["preferred_work_format"] = "remote"
    elif "офис" in lowered:
        params["preferred_work_format"] = "office"
    elif "гибрид" in lowered:
        params["preferred_work_format"] = "hybrid"

    match = re.search(r"(?:митинг|meeting)\w*\s*[:\-]?\s*(\d+)", lowered)
    if match:
        params["meeting_love_level"] = max(0, min(10, int(match.group(1))))

    if "мем" in lowered:
        params["humor_level"] = "max_memes"
    elif "сух" in lowered:
        params["humor_level"] = "dry"
    else:
        params["humor_level"] = "moderate"

    if "свят" in lowered:
        params["deadline_attitude"] = "sacred"
    elif "фантик" in lowered:
        params["deadline_attitude"] = "relaxed"

    if "ракета" in lowered:
        params["dev_speed"] = "rocket"
    elif "велосипед" in lowered:
        params["dev_speed"] = "bike"
    elif "черепах" in lowered:
        params["dev_speed"] = "turtle"

    rituals = []
    for line in text.splitlines():
        if "ритуал" in line.lower() or "ритуалы" in line.lower():
            parts = re.split(r"[:,]", line, maxsplit=1)
            if len(parts) == 2:
                rituals.extend([p.strip() for p in parts[1].split(",") if p.strip()])
    if rituals:
        params["rituals"] = rituals

    return params
