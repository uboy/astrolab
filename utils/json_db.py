import json
import asyncio
from pathlib import Path

_read_lock = asyncio.Lock()
_write_lock = asyncio.Lock()

async def read_json(file_path: str):
    """
    Асинхронное чтение JSON.
    Если файла нет или битый JSON, создаётся пустой словарь.
    """
    path = Path(file_path)
    if not path.exists():
        await write_json(file_path, {})
        return {}

    async with _read_lock:
        try:
            content = path.read_text(encoding="utf-8")
            if not content.strip():
                await write_json(file_path, {})
                return {}
            return json.loads(content)
        except json.JSONDecodeError:
            await write_json(file_path, {})
            return {}

async def write_json(file_path: str, data):
    """
    Асинхронная безопасная запись JSON.
    """
    async with _write_lock:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
