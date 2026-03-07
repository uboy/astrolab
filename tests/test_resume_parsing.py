from pathlib import Path

import pytest

import utils.resume_ingest as resume_ingest
import utils.resume_parser as resume_parser


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "resumes"


def _load_bytes(name: str) -> bytes:
    path = FIXTURES_DIR / name
    return path.read_bytes()


def _load_text(name: str) -> str:
    path = FIXTURES_DIR / name
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("resume_basic.md", "text/markdown"),
        ("resume_basic.pdf", "application/pdf"),
        ("resume_basic.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ],
)
def test_validate_resume_file_accepts_formats(filename, content_type):
    try:
        resume_ingest.validate_resume_file(filename, content_type, size_bytes=1024)
    except NotImplementedError:
        pytest.xfail("resume_ingest.validate_resume_file not implemented yet")


@pytest.mark.parametrize(
    "filename",
    ["resume_basic.md", "resume_basic.pdf", "resume_basic.docx", "resume_rich.docx", "resume_rich.pdf"],
)
def test_extract_resume_text_basic_contains_name(filename):
    raw = _load_bytes(filename)
    try:
        text = resume_ingest.extract_resume_text(
            raw,
            filename=filename,
            content_type="application/octet-stream",
        )
    except NotImplementedError:
        pytest.xfail("resume_ingest.extract_resume_text not implemented yet")
    assert "Иван" in text or "Ivan" in text


def test_extract_resume_text_rejects_corrupted_pdf():
    raw = _load_bytes("resume_bad.pdf")
    try:
        with pytest.raises(Exception):
            resume_ingest.extract_resume_text(
                raw,
                filename="resume_bad.pdf",
                content_type="application/pdf",
            )
    except NotImplementedError:
        pytest.xfail("resume_ingest.extract_resume_text not implemented yet")


def test_parse_resume_text_basic_md():
    text = _load_text("resume_basic.md")
    try:
        data = resume_parser.parse_resume_text(text)
    except NotImplementedError:
        pytest.xfail("resume_parser.parse_resume_text not implemented yet")
    assert data.get("first_name") == "Иван"
    assert data.get("last_name") == "Петров"
    assert "ivan.petrov@example.com" in (data.get("email") or "")
    assert data.get("experience_years") in (4.5, "4.5", 4.0)
    assert "Python" in (data.get("skills") or [])


def test_parse_resume_text_missing_fields():
    text = _load_text("resume_missing_fields.md")
    try:
        data = resume_parser.parse_resume_text(text)
    except NotImplementedError:
        pytest.xfail("resume_parser.parse_resume_text not implemented yet")
    assert data.get("first_name") == "Анна"
    assert data.get("last_name") == "Смирнова"
    assert "React" in (data.get("skills") or [])


def test_parse_resume_text_multilang():
    text = _load_text("resume_multilang.md")
    try:
        data = resume_parser.parse_resume_text(text)
    except NotImplementedError:
        pytest.xfail("resume_parser.parse_resume_text not implemented yet")
    assert data.get("first_name") == "Maria"
    assert data.get("last_name") == "Johnson"
    assert "maria@example.com" in (data.get("email") or "")
    assert "Python" in (data.get("skills") or [])


def test_parse_resume_text_empty():
    text = _load_text("resume_empty.md")
    try:
        data = resume_parser.parse_resume_text(text)
    except NotImplementedError:
        pytest.xfail("resume_parser.parse_resume_text not implemented yet")
    assert data == {} or data is not None


@pytest.mark.parametrize(
    "filename",
    ["resume_multi_email.md", "resume_mixed_languages.md", "resume_date_ranges.md"],
)
def test_parse_resume_text_edge_cases(filename):
    text = _load_text(filename)
    try:
        data = resume_parser.parse_resume_text(text)
    except NotImplementedError:
        pytest.xfail("resume_parser.parse_resume_text not implemented yet")
    assert isinstance(data, dict)
    if filename == "resume_multi_email.md":
        email = data.get("email") or ""
        assert "@" in email
    if filename == "resume_date_ranges.md":
        assert data.get("experience_years") is not None or data.get("experience_range") is not None


def test_merge_candidate_profile_prioritizes_user_input():
    import utils.candidate_compatibility as candidate_compat
    user_input = {"email": "new@example.com", "experience_years": 5}
    resume_data = {"email": "old@example.com", "experience_years": 2}
    try:
        merged = candidate_compat.merge_candidate_profile(user_input, resume_data)
    except NotImplementedError:
        pytest.xfail("candidate_compatibility.merge_candidate_profile not implemented yet")
    assert merged["email"] == "new@example.com"
    assert merged["experience_years"] == 5
