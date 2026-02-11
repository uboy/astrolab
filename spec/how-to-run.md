# How to run

## Prerequisites
- Python 3.11+ (Dockerfile uses `python:3.11-slim`). Evidence: `Dockerfile`.
- Telegram bot token and chat access. Evidence: `utils/config.py:Settings.BOT_TOKEN`.
- Ollama server reachable at `OLLAMA_URL` with the configured model(s). Evidence: `utils/config.py:Settings.OLLAMA_URL`, `utils/config.py:Settings.OLLAMA_MODEL`, `utils/ollama.py:ask_ollama`.

## Install steps
- Create a virtual environment and install dependencies from `requirements.txt`. Evidence: `requirements.txt`.

## Config / environment variables
- Required (must be set):
  - `BOT_TOKEN` (Telegram bot token). Evidence: `utils/config.py:Settings.BOT_TOKEN`.
  - `OLLAMA_URL` (Ollama endpoint; `/api/generate` expected for text). Evidence: `utils/config.py:Settings.OLLAMA_URL`, `utils/ollama.py:ask_ollama`.
  - `OLLAMA_MODEL` (default text model). Evidence: `utils/config.py:Settings.OLLAMA_MODEL`.
  - `RATE_LIMIT_PER_MIN`, `RATE_LIMIT_PER_HOUR`, `FREE_MESSAGES_COUNT`, `ADMINS`. Evidence: `utils/config.py:Settings`.
    Note: rate limit env vars are currently unused; limits are hard-coded in `utils/constants.py`. Evidence: `utils/rate_limit.py:check_rate_limit`, `utils/constants.py:OLLAMA_PER_MIN`, `utils/constants.py:OTHER_PER_MIN`.
- Optional:
  - `OLLAMA_VISION_MODEL` (defaults to `qwen3-vl:32b`). Evidence: `utils/config.py:Settings.OLLAMA_VISION_MODEL`.
  - `TIMEZONE` (defaults to `local`). Evidence: `utils/config.py:Settings.TIMEZONE`, `utils/subscription_scheduler.py:_detect_tz`.
  - `LOG_LEVEL` (defaults to `ERROR_WARNING`). Evidence: `utils/config.py:Settings.LOG_LEVEL`, `utils/logging_config.py:get_log_level`.

## Run locally
- `python main.py` (starts polling and the subscription scheduler). Evidence: `main.py:main`.

## Run with Docker
- Build and run the container; volumes should mount `data/` and `logs/` if you want persistence. Evidence: `Dockerfile`, `docker-compose.yml`.

## Run tests
- Unknown (no tests found in repo).
