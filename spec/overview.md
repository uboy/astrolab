# Overview

## Purpose
- Telegram bot that serves paid/free fortune-telling features (weekly horoscope, numerology, compatibility, photo destiny, zodiac quiz, luck reset) via aiogram message handlers and menu buttons. Evidence: `handlers/horoscope.py:start_horoscope`, `handlers/numerology.py:start_numerology`, `handlers/compatibility.py:start_compatibility`, `handlers/photo_destiny.py:start_photo_destiny`, `handlers/curse.py:start_quiz`, `handlers/curse_detection.py:start_curse_detection`.
- Integrates with Ollama for text and vision responses using HTTP calls and formats output for Telegram HTML. Evidence: `utils/ollama.py:ask_ollama`, `utils/message_helpers.py:process_ollama_with_progress`.
- Tracks user balances, usage history, and subscriptions in JSON files and enforces per-feature rate limits. Evidence: `utils/user_helpers.py:get_user`, `utils/json_db.py:read_json`, `utils/rate_limit.py:check_rate_limit`.
- Provides admin-only tooling to inspect users, send broadcasts, manage subscriptions, and update prices. Evidence: `handlers/admin.py:admin_menu`, `handlers/admin.py:user_actions`, `handlers/admin.py:admin_set_price`.

## Primary user flows
- Start bot, see main menu with priced buttons, pick a service, provide inputs (dates/names/photos). Ollama-backed services return generated responses with balance; non-Ollama services return plain responses (no balance footer). Evidence: `keyboards/menus.py:menu_for`, `handlers/horoscope.py:get_birthdate`, `handlers/compatibility.py:run_compatibility`, `handlers/numerology.py:get_birthdate`, `handlers/photo_destiny.py:process_photo`, `handlers/curse_detection.py:handle_curse_decision`, `handlers/base.py:choose_method`.
- Top up balance via simulated payment flow (amount -> method -> random success/fail). Evidence: `handlers/base.py:payment_start`, `handlers/base.py:choose_method`.
- Subscribe to daily horoscope by entering birthdate; receive scheduled daily messages. Evidence: `handlers/subscription.py:start_subscribe`, `utils/subscription_scheduler.py:run_subscription_scheduler`.
- Purchase premium time-limited multiplier via balance deduction. Evidence: `handlers/base.py:premium_start`, `utils/user_helpers.py:activate_premium`.
- Admin opens admin menu, browses users, updates subscription time, sends broadcasts, and edits prices. Evidence: `handlers/admin.py:admin_home`, `handlers/admin.py:_show_users_page`, `handlers/admin.py:admin_set_time`, `handlers/admin.py:admin_broadcast_send`, `handlers/admin.py:admin_set_price`.

## Feature matrix
| Feature | Inputs | Price key | Uses Ollama | Rate limited |
| --- | --- | --- | --- | --- |
| Horoscope | Birthdate (ДД.MM.ГГГГ) | `horoscope` | Yes | Yes |
| Compatibility | Names/dates or photos | `compatibility` | Yes | Yes |
| Numerology | Name + birthdate | `numerology` | Yes | Yes |
| Photo destiny | Photo upload | `photo_destiny` | Yes | Yes |
| Zodiac quiz | Multiple-choice answers | `zodiac_quiz` | Yes | Yes |
| Luck reset | Yes/No decision | `luck_reset` | No | Yes |
| Subscription | Birthdate, scheduled send | `subscription` | Yes (scheduler) | No |
| Premium | Plan selection | `premium_1d/2d/3d` | No | No |
| Payments | Amount + method | N/A | No | No |
Evidence: `handlers/horoscope.py`, `handlers/compatibility.py`, `handlers/numerology.py`, `handlers/photo_destiny.py`, `handlers/curse.py`, `handlers/curse_detection.py`, `handlers/subscription.py`, `handlers/base.py`, `utils/rate_limit.py:check_rate_limit`, `utils/constants.py:OLLAMA_FEATURES`.

## Limitations
- Real payment processing is not implemented; payments are simulated with a random success outcome. Evidence: `handlers/base.py:choose_method`.
- Long polling only; webhooks are not configured. Evidence: `main.py:main`.
- Persistence is file-based JSON, which may not scale for large user counts. Evidence: `utils/json_db.py:read_json`, `utils/json_db.py:write_json`.
- Ollama must be reachable for AI features; failures return fallback text. Evidence: `utils/ollama.py:ask_ollama`.

## Non-goals
- Real payment processing is not implemented; payment is simulated with a random success outcome. Evidence: `handlers/base.py:choose_method`.
- No web UI or REST API; only Telegram polling handlers are used. Evidence: `main.py:main`, `handlers/*.py`.
- No database server; persistence is file-based JSON in `data/`. Evidence: `utils/json_db.py:read_json`, `utils/prices.py:PRICES_FILE`.
- No webhook support; bot uses long polling. Evidence: `main.py:main`.

## Open Questions
- None.
