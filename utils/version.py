from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = PROJECT_ROOT / "VERSION"


def get_bot_version(short: bool = True) -> str:
    env_version = os.getenv("BOT_VERSION", "").strip()
    if env_version:
        return env_version[:8] if short else env_version

    file_version = _read_version_file()
    if file_version:
        return file_version[:8] if short else file_version

    git_version = get_git_sha()
    return git_version[:8] if short else git_version


def get_git_sha() -> str:
    git_dir = PROJECT_ROOT / ".git"
    head_path = git_dir / "HEAD"
    if not head_path.exists():
        return "unknown"
    head = head_path.read_text(encoding="utf-8").strip()
    if head.startswith("ref:"):
        ref = head.split(" ", 1)[1].strip()
        ref_path = git_dir / ref
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
        packed = git_dir / "packed-refs"
        if packed.exists():
            ref_sha = _read_packed_ref(packed, ref)
            if ref_sha:
                return ref_sha
        return "unknown"
    return head


def _read_version_file() -> str:
    if not VERSION_FILE.exists():
        return ""
    value = VERSION_FILE.read_text(encoding="utf-8").strip()
    return value


def _read_packed_ref(path: Path, ref: str) -> str:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or line.startswith("^"):
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].strip() == ref:
            return parts[0].strip()
    return ""
