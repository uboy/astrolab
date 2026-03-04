from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    OLLAMA_URL: str
    OLLAMA_MODEL: str
    OLLAMA_VISION_MODEL: str = "qwen3-vl:32b"
    TIMEZONE: str = "local"
    RATE_LIMIT_PER_MIN: int
    RATE_LIMIT_PER_HOUR: int
    FREE_MESSAGES_COUNT: int
    ADMINS: List[int]
    LOG_LEVEL: str = "ERROR_WARNING"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()
