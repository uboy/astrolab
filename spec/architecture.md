# Architecture

## High-level components
- Entry point initializes bot, registers routers, and starts polling; also launches subscription scheduler in a background task. Evidence: `main.py:main`.
- Handlers implement feature flows: horoscope, compatibility, numerology, photo destiny, zodiac quiz, luck reset, subscription, admin, and payments. Evidence: `handlers/*.py` (e.g., `handlers/horoscope.py`, `handlers/base.py`).
- Utilities provide configuration, persistence, rate limiting, pricing, Ollama integration, and message helpers. Evidence: `utils/config.py`, `utils/json_db.py`, `utils/rate_limit.py`, `utils/prices.py`, `utils/ollama.py`, `utils/message_helpers.py`.
- Keyboards render the main menu and payment menus with dynamic pricing. Evidence: `keyboards/menus.py:menu_for`.

## Key data models
- User record in `data/users.json` contains `free_count`, `paid_count`, `history`, `actions`, `rate`, `subscription`, `premium`, `profile`, and timestamps. Evidence: `utils/user_helpers.py:get_user`.
- Subscription data includes `active`, `time`, `birthdate`, and `last_sent`. Evidence: `utils/user_helpers.py:_default_subscription`, `utils/subscription_scheduler.py:_process_once`.
- Premium data includes `active` and `until` timestamp. Evidence: `utils/user_helpers.py:_default_premium`, `utils/user_helpers.py:activate_premium`.
- Prices are stored in `data/prices.json` with defaults from constants. Evidence: `utils/prices.py:PRICES_FILE`, `utils/constants.py:DEFAULT_PRICES`.
- Ollama timing stats stored in `data/ollama_stats.json` with per-model duration samples. Evidence: `utils/ollama_stats.py:DATA_FILE`, `utils/ollama_stats.py:record_duration`.

## Control flow
- User message arrives -> aiogram router -> handler validates input and checks balance/rate limits -> optional balance deduction -> Ollama call -> response formatting -> Telegram reply. Evidence: `handlers/horoscope.py:get_birthdate`, `utils/pricing_helpers.py:ensure_balance_and_charge`, `utils/ollama.py:ask_ollama`, `utils/message_helpers.py:format_response_with_balance`.
- Payment flow: user selects amount and method -> simulated delay -> random success/fail -> update user paid balance and log action. Evidence: `handlers/base.py:choose_amount`, `handlers/base.py:choose_method`, `utils/user_helpers.py:log_user_action`.
- Subscription scheduler: background task runs every 60 seconds -> iterates active subscribers -> checks due time and balance -> sends daily horoscope -> charges balance and updates `last_sent`. Evidence: `utils/subscription_scheduler.py:run_subscription_scheduler`, `utils/subscription_scheduler.py:_process_once`.

## Subscription timing rules
- If `subscription.time` is `auto`/empty, the send time is deterministically distributed within 11:00-19:00 using an MD5 hash of the user ID. Evidence: `utils/subscription_scheduler.py:_default_send_time`.
- If `subscription.time` is present, it is parsed as `HH:MM` and clamped to valid ranges. Evidence: `utils/subscription_scheduler.py:_parse_time`.
- Scheduler time zone comes from `TIMEZONE` (or local if unset/invalid). Evidence: `utils/subscription_scheduler.py:_detect_tz`.

## Dependencies and integration points
- Telegram Bot API via aiogram. Evidence: `main.py`, `handlers/*` (aiogram imports).
- Ollama HTTP API via httpx, using `/api/generate` or `/api/chat`. Evidence: `utils/ollama.py:ask_ollama`.
- Pydantic settings for environment configuration. Evidence: `utils/config.py:Settings`.
- Local filesystem for JSON persistence and logs. Evidence: `utils/json_db.py:write_json`, `utils/logging_config.py:setup_logging`.

## Open Questions
- None.
