import json
from utils.json_db import read_json, write_json
from utils.constants import DEFAULT_PRICES
from pathlib import Path

PRICES_FILE = "data/prices.json"


def _ensure_default_sync() -> dict:
    path = Path(PRICES_FILE)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(DEFAULT_PRICES, ensure_ascii=False, indent=2), encoding="utf-8")
        return DEFAULT_PRICES.copy()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_PRICES.copy()


async def get_prices() -> dict:
    data = await read_json(PRICES_FILE)
    if not data:
        data = DEFAULT_PRICES.copy()
        await write_json(PRICES_FILE, data)
    return data


def get_prices_sync() -> dict:
    return _ensure_default_sync()


async def set_price(feature: str, value: int) -> None:
    data = await get_prices()
    data[feature] = max(0, int(value))
    await write_json(PRICES_FILE, data)
