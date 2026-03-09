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

    location_match = re.search(r"(?:локация|локации|location)\s*[:\-]?\s*([^\n]+)", text, re.IGNORECASE)
    if location_match:
        parts = re.split(r"[,;/|]", location_match.group(1))
        locations = [p.strip(" .;") for p in parts if p.strip(" .;")]
        if locations:
            params["preferred_locations"] = locations[:5]

    element_match = re.search(r"(?:стихия|element)\s*[:\-]?\s*(огонь|вода|воздух|земля|fire|water|air|earth)", lowered)
    if element_match:
        value = element_match.group(1)
        element_map = {
            "огонь": "fire",
            "вода": "water",
            "воздух": "air",
            "земля": "earth",
            "fire": "fire",
            "water": "water",
            "air": "air",
            "earth": "earth",
        }
        params["cosmic_element"] = element_map.get(value, value)

    destiny_match = re.search(r"(?:число\s*судьбы|destiny\s*number)\s*[:\-]?\s*(\d{1,2})", lowered)
    if destiny_match:
        num = int(destiny_match.group(1))
        params["company_destiny_number"] = max(1, min(9, num))

    tarot_match = re.search(r"(?:карта\s*таро|tarot\s*card)\s*[:\-]?\s*([^\n,.;]+)", text, re.IGNORECASE)
    if tarot_match:
        params["company_tarot_card"] = tarot_match.group(1).strip()

    rituals = []
    for line in text.splitlines():
        if "ритуал" in line.lower() or "ритуалы" in line.lower():
            match = re.search(r"ритуал\w*\s*:\s*(.+)$", line, re.IGNORECASE)
            if match:
                rituals.extend([p.strip(" .;") for p in match.group(1).split(",") if p.strip(" .;")])
    if rituals:
        params["rituals"] = rituals

    return params
