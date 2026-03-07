from utils.button_matchers import is_compatibility_button, is_candidate_compatibility_button
from utils.constants import BTN_COMPATIBILITY, BTN_CANDIDATE_COMPATIBILITY


def test_compatibility_button_matches_only_compatibility():
    assert is_compatibility_button(BTN_COMPATIBILITY)
    assert is_compatibility_button(f"{BTN_COMPATIBILITY} (1 у.е)")
    assert not is_compatibility_button(BTN_CANDIDATE_COMPATIBILITY)
    assert not is_compatibility_button(f"{BTN_CANDIDATE_COMPATIBILITY} (1 у.е)")


def test_candidate_compatibility_button_matches_only_candidate():
    assert is_candidate_compatibility_button(BTN_CANDIDATE_COMPATIBILITY)
    assert is_candidate_compatibility_button(f"{BTN_CANDIDATE_COMPATIBILITY} (1 у.е)")
    assert not is_candidate_compatibility_button(BTN_COMPATIBILITY)
    assert not is_candidate_compatibility_button(f"{BTN_COMPATIBILITY} (1 у.е)")
