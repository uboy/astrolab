# Behavior

## Observable behaviors
- Telegram bot responds to menu buttons and user inputs (text, dates, photos) to run horoscope, numerology, compatibility, photo destiny, zodiac quiz, luck reset, payments, subscription, and admin flows. Evidence: `handlers/horoscope.py`, `handlers/numerology.py`, `handlers/compatibility.py`, `handlers/photo_destiny.py`, `handlers/curse.py`, `handlers/curse_detection.py`, `handlers/base.py`, `handlers/subscription.py`, `handlers/admin.py`.
- Ollama-backed flows return Telegram messages with HTML formatting and a balance footer; non-Ollama flows often send plain text without balance. Evidence: `utils/message_helpers.py:format_response_with_balance`, `handlers/horoscope.py:get_birthdate`, `handlers/compatibility.py:run_compatibility`, `handlers/numerology.py:get_birthdate`, `handlers/photo_destiny.py:process_photo`, `handlers/curse.py:handle_quiz_answer`, `handlers/base.py:choose_method`, `handlers/subscription.py:handle_birthdate`, `handlers/admin.py:admin_home`.
- Some Ollama-backed flows show a progress animation (GIF + progress bar) and delete it after completion. Evidence: `utils/message_helpers.py:process_ollama_with_progress`.

## Inputs / outputs and side effects
- Inputs: Telegram message text, user profile data, and photo uploads. Evidence: `handlers/*` (e.g., `handlers/photo_destiny.py:process_photo`).
- External calls: HTTP POST to Ollama `/api/generate` or `/api/chat` depending on whether images/files are present. Evidence: `utils/ollama.py:ask_ollama`, `utils/ollama.py:_get_chat_url`.
- Side effects: JSON files updated for users, prices, and Ollama timing stats; log files created under `logs/`. Evidence: `utils/json_db.py:write_json`, `utils/prices.py:PRICES_FILE`, `utils/ollama_stats.py:record_duration`, `utils/logging_config.py:setup_logging`.
- Background task: subscription scheduler runs every 60 seconds and sends daily messages when due. Evidence: `main.py:main`, `utils/subscription_scheduler.py:run_subscription_scheduler`.

## Error handling and edge cases
- Invalid date formats, underage/overage checks, and invalid names produce user-facing errors and stop the flow. Evidence: `handlers/horoscope.py:get_birthdate`, `handlers/numerology.py:get_birthdate`, `handlers/numerology.py:get_name`.
- Rate limits reject requests and respond with a wait message. Evidence: `utils/rate_limit.py:check_rate_limit`, `handlers/horoscope.py:get_birthdate`.
- Ollama errors return fallback responses (timeout, HTTP errors, empty output). Evidence: `utils/ollama.py:ask_ollama`.
- Photo processing errors are caught and reported to the user. Evidence: `handlers/photo_destiny.py:process_photo`.
- JSON read errors or missing files are recovered by overwriting with empty objects. Evidence: `utils/json_db.py:read_json`.

## Message formatting rules
- Ollama-backed features send HTML-formatted messages and append the balance footer via `format_response_with_balance`. Evidence: `utils/message_helpers.py:format_response_with_balance`, `handlers/horoscope.py:get_birthdate`, `handlers/compatibility.py:run_compatibility`, `handlers/numerology.py:get_birthdate`, `handlers/photo_destiny.py:process_photo`, `handlers/curse.py:handle_quiz_answer`.
- Non-Ollama flows (payments, admin, subscription confirmations, luck reset decisions) send plain text and usually omit balance. Evidence: `handlers/base.py:choose_method`, `handlers/admin.py:admin_home`, `handlers/subscription.py:handle_birthdate`, `handlers/curse_detection.py:handle_curse_decision`.
- Subscription scheduler sends HTML-formatted messages for daily horoscopes. Evidence: `utils/subscription_scheduler.py:_process_once`.

## Admin commands surface
- Entry: `Админка` button opens admin menu. Evidence: `handlers/admin.py:admin_menu`, `utils/constants.py:BTN_ADMIN`.
- User list navigation: next/previous page and user selection by ID. Evidence: `handlers/admin.py:browse_users`, `utils/constants.py:BTN_ADMIN_NEXT_PAGE`, `utils/constants.py:BTN_ADMIN_PREV_PAGE`.
- User actions: view profile/history, reset limits, subscribe/unsubscribe, set delivery time, send message, delete user. Evidence: `handlers/admin.py:user_actions`, `utils/constants.py:BTN_ADMIN_USER_INFO`, `utils/constants.py:BTN_ADMIN_USER_HISTORY`, `utils/constants.py:BTN_ADMIN_USER_RESET`, `utils/constants.py:BTN_ADMIN_USER_SUBSCRIBE`, `utils/constants.py:BTN_ADMIN_USER_UNSUBSCRIBE`, `utils/constants.py:BTN_ADMIN_USER_SET_TIME`, `utils/constants.py:BTN_ADMIN_USER_SEND`, `utils/constants.py:BTN_ADMIN_USER_DELETE`.
- Broadcasts and pricing: send to all subscribers, view/edit prices, view settings/logs. Evidence: `handlers/admin.py:admin_home`, `handlers/admin.py:admin_set_price`, `utils/constants.py:BTN_ADMIN_BROADCAST`, `utils/constants.py:BTN_ADMIN_PRICES`, `utils/constants.py:BTN_ADMIN_SETTINGS`, `utils/constants.py:BTN_ADMIN_LOGS`.

## Assumptions
- Required environment variables are present (bot token, Ollama URL/model, rate limits, admins). Evidence: `utils/config.py:Settings`.
- Ollama server is reachable at the configured URL and supports `/api/generate` and `/api/chat`. Evidence: `utils/ollama.py:ask_ollama`.
- Local filesystem is writable for `data/` and `logs/`. Evidence: `utils/json_db.py:write_json`, `utils/logging_config.py:setup_logging`.
- Timezone string is valid for `zoneinfo` or local timezone is available. Evidence: `utils/subscription_scheduler.py:_detect_tz`.

## Open Questions
- None.
