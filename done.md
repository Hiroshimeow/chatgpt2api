# DONE.md

Completed implementation summaries go here.

## 2026-06-29 - GPT backend/session pool

Implemented a narrow GPT backend pool for `OpenAIBackendAPI` sessions.

Changed files:

- `services/openai_backend_pool.py`
  - Added `OpenAIBackendPool`.
  - Added `lease_openai_backend(...)` context manager.
  - Added `BackendTokenRef` / `backend_token_ref(...)` so callers can carry a token without constructing a backend session.
  - Reuses an idle backend for the same access token.
  - Retires a backend after 10 high-level leases/calls.
  - Does not share the same backend object while it is already in use.
  - Resets `progress_callback` on release.

- `services/protocol/conversation.py`
  - Text path now leases pooled backend sessions.
  - Image path now leases pooled backend sessions and passes per-request progress callback through the lease.

- `services/protocol/openai_search.py`
  - Search path now leases a pooled backend session.

- `services/protocol/web_search_tool.py`
  - Web-search tool path now leases a pooled backend session.

- `services/protocol/anthropic_v1_messages.py`
  - Message request now uses a lightweight token ref instead of eagerly constructing a backend session.

- `test/test_openai_backend_pool.py`
  - Added tests for idle reuse, max-lease retirement, non-sharing while in use, and progress callback reset.

Evidence:

- `python -m compileall -q services/openai_backend_pool.py services/protocol/conversation.py services/protocol/openai_search.py services/protocol/web_search_tool.py services/protocol/anthropic_v1_messages.py test/test_openai_backend_pool.py` => PASS
- `python -m unittest test.test_openai_backend_pool -v` => 3 tests PASS
- `python -m unittest test.test_openai_backend_pool test.test_chat_completion_cache test.test_v1_models -v` => 32 tests PASS

Notes:

- Remote `origin/main` matched local `HEAD` before implementation; no upstream update was available.
- Existing dirty files before this task were not cleaned: `config.json`, `services/account_service.py`, `web/package-lock.json`.
- Rate limiter/circuit breaker and extra privacy boundary work are intentionally out of scope for this task.

## 2026-06-29 - Vietnamese localization pass

Scope:

- Rewrote README and docs/changelog into Vietnamese.
- Applied a broad Vietnamese dictionary pass across UI/API/docs messages.
- Kept core identifiers and status enum values unchanged where changing them could break stored account data.
- Did not stage local config or generated lockfile noise.

Evidence:

- Backend compileall: PASS.
- `test.test_openai_backend_pool`: PASS.
- `test.test_v1_models`: PASS.
- Frontend `npm run build`: PASS.
- Full unittest discovery was attempted, but it is not clean in this environment because discovery imports `test/utils.py` as `utils` and shadows the real package; several HTTP tests also fail with local 401 auth config. This is recorded but not treated as a localization syntax failure.

Known limitation:

- Some deeper backend comments/messages and internal status values still contain CJK text. A second pass should introduce a proper i18n/display mapping instead of translating storage/status enum values directly.
