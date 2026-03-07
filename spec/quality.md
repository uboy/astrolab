# Quality

## Testing status
- No testing dependencies are listed, and no test entry points are referenced in runtime code. Evidence: `requirements.txt`, `main.py:main`.
- Test suite location and runner are not defined in the repository root. Evidence: `README.md` (no test section).

## Performance considerations / bottlenecks
- Each user interaction reads/writes `data/users.json` and updates rate/balance, which may become a bottleneck as the file grows. Evidence: `utils/user_helpers.py:get_user`, `utils/json_db.py:read_json`, `utils/json_db.py:write_json`.
- Subscription scheduler scans all users every 60 seconds and may scale poorly with large user counts. Evidence: `utils/subscription_scheduler.py:run_subscription_scheduler`, `utils/subscription_scheduler.py:_process_once`.
- Ollama requests use long timeouts (300-420s) and can block processing per request, increasing latency. Evidence: `utils/ollama.py:ask_ollama`.

## Data retention & privacy
- User profiles and activity history (including Telegram identifiers) are stored in plain JSON. Evidence: `utils/user_helpers.py:_extract_profile`, `utils/user_helpers.py:get_user`, `utils/json_db.py:write_json`.
- No retention policy or anonymization is implemented; data is kept indefinitely unless manually deleted. Evidence: `utils/user_helpers.py:save_user`, `handlers/admin.py:admin_delete_user`.

## Security considerations and risky patterns
- User profiles and activity history (including Telegram identifiers) are stored in plain JSON without encryption. Evidence: `utils/user_helpers.py:_extract_profile`, `utils/user_helpers.py:get_user`, `utils/json_db.py:write_json`.
- Admin access relies solely on user IDs from environment configuration. Evidence: `handlers/admin.py:is_admin`, `utils/config.py:Settings.ADMINS`.
- A merge conflict marker remains in `MSG_ABOUT_COMPANY`, which will cause a syntax error at import time. Evidence: `utils/constants.py:MSG_ABOUT_COMPANY`.
- `utils/message_helpers.py` references `data/magic_ball.png`, but the file is not present in `data/`, which can cause missing-asset behavior. Evidence: `utils/message_helpers.py:process_ollama_with_progress`, `data/` directory listing.

## Known discrepancies (spec vs implementation)
- Rate limit env vars are required by configuration but not actually used by the rate limiting logic, which relies on hard-coded constants. Evidence: `utils/config.py:Settings`, `utils/rate_limit.py:check_rate_limit`, `utils/constants.py:OLLAMA_PER_MIN`, `utils/constants.py:OTHER_PER_MIN`.
- Only Ollama-backed flows include the balance footer; many non-Ollama responses are plain text. Evidence: `utils/message_helpers.py:format_response_with_balance`, `handlers/base.py:choose_method`, `handlers/subscription.py:handle_birthdate`, `handlers/admin.py:admin_home`.

## Open Questions
- None.
