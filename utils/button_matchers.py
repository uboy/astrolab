from __future__ import annotations

from utils.constants import BTN_COMPATIBILITY, BTN_CANDIDATE_COMPATIBILITY


def is_compatibility_button(text: str | None) -> bool:
    if not text:
        return False
    clean = text.split(" (", 1)[0].strip()
    return clean == BTN_COMPATIBILITY


def is_candidate_compatibility_button(text: str | None) -> bool:
    if not text:
        return False
    clean = text.split(" (", 1)[0].strip()
    return clean == BTN_CANDIDATE_COMPATIBILITY
