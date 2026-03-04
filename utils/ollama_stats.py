import asyncio
import time
from utils.json_db import read_json, write_json

DATA_FILE = "data/ollama_stats.json"
MAX_SAMPLES = 20
FALLBACK_SECONDS = 60.0


async def record_duration(model: str, duration: float) -> None:
    stats = await read_json(DATA_FILE)
    model_stats = stats.get(model, {"durations": []})
    durations = model_stats.get("durations", [])
    durations.append(duration)
    if len(durations) > MAX_SAMPLES:
        durations = durations[-MAX_SAMPLES:]
    model_stats["durations"] = durations
    model_stats["updated_at"] = time.time()
    stats[model] = model_stats
    await write_json(DATA_FILE, stats)


async def estimate_duration(model: str) -> float:
    stats = await read_json(DATA_FILE)
    model_stats = stats.get(model)
    if not model_stats:
        return FALLBACK_SECONDS
    durations = model_stats.get("durations") or []
    if not durations:
        return FALLBACK_SECONDS
    return sum(durations) / len(durations)
