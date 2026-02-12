from __future__ import annotations

import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_bot_version(short: bool = True) -> str:
    env_version = os.getenv("BOT_VERSION", "").strip()
    if env_version and env_version.lower() != "unknown":
        return env_version[:8] if short else env_version

    git_version = get_git_sha()
    if git_version != "unknown":
        return git_version[:8] if short else git_version

    return "unknown"


def get_git_sha() -> str:
    # Fast path: ask git directly if available.
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except Exception:
        pass

    # Fallback for environments where git binary is unavailable.
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


def _read_packed_ref(path: Path, ref: str) -> str:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#") or line.startswith("^"):
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].strip() == ref:
            return parts[0].strip()
    return ""
