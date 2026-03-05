import json
from utils.json_db import read_json, write_json
from utils.constants import DEFAULT_PRICES
from pathlib import Path

PRICES_FILE = "data/prices.json"


def _ensure_default_sync() -> dict:
    path = Path(PRICES_FILE)
    data = DEFAULT_PRICES.copy()
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update(loaded)
        except Exception:
            pass
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return data


async def get_prices() -> dict:
    data = await read_json(PRICES_FILE)
    changed = False
    if not isinstance(data, dict):
        data = {}
    merged = DEFAULT_PRICES.copy()
    merged.update(data)
    if merged != data:
        changed = True
    if changed:
        await write_json(PRICES_FILE, merged)
    return merged


def get_prices_sync() -> dict:
    return _ensure_default_sync()


async def set_price(feature: str, value: int) -> None:
    data = await get_prices()
    data[feature] = max(0, int(value))
    await write_json(PRICES_FILE, data)
