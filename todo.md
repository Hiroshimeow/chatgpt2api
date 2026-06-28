# TODO.md - Agent Entry Checklist

This file is the first document every agent must read before working in this repository.

## 1. Repository freshness check

Before changing code:

1. Run `git status --short --branch` and record dirty files.
2. Run `git remote -v` and confirm the upstream repository.
3. Run `git fetch --dry-run origin` or `git ls-remote origin refs/heads/main` without pulling.
4. Compare local `HEAD` with `origin/main`.
5. If upstream has newer commits, inspect what changed before pulling:
   - feature area touched
   - security/performance relevance
   - breaking changes
   - overlap with local dirty files
6. Decide whether the update is worth applying now.
7. If pulling/merging is needed, estimate conflict risk first:
   - list local modified files
   - list upstream changed files
   - identify direct overlaps
   - state likely conflict files and resolution strategy

Do not pull automatically unless the task explicitly requires it.

## 2. Work planning flow

1. Add active work to `plan.md` before implementation.
2. Keep the plan scoped and concrete.
3. After completing a task, move the implementation summary and evidence into `done.md`.
4. Keep `plan.md` focused on unfinished work only.

## 3. Current engineering priority

Primary focus: performance and GPT-side safety for the ChatGPT backend adapter.

Ignore local machine hardening unless explicitly requested.

Current active priority:

- Implement GPT backend/session pool.
- Reuse a backend session for up to 10 high-level API calls.
- Do not implement account rate limiter/circuit breaker yet.
- Do not implement extra privacy boundary work yet.

## Known issue: text model auto-routes/falls back to GPT-5.3-mini

Problem:

- Text chat requests may report or behave like `GPT-5.3-mini` even when the client passes `gpt-5-5` / `gpt-5.5` / `gpt-5-5-thinking`.
- Upstream ChatGPT web backend appears to auto-route text models; the `model` field in `/backend-api/conversation` is not a hard guarantee.
- Invalid/random model names can still receive a response because ChatGPT backend may route anyway.

Upstream issue references checked:

- https://github.com/basketikun/chatgpt2api/issues/312
  - Plus account output changed from 5.5 to GPT-5.3-mini.
  - Maintainer said web model degradation/auto-routing is normal.
- https://github.com/basketikun/chatgpt2api/issues/275
  - Users reported `gpt-5-5` / Plus still becoming GPT-5.3-mini.
  - Maintainer said it cannot be solved reliably because web backend can route even Pro accounts to mini.
- https://github.com/basketikun/chatgpt2api/issues/303
  - User showed arbitrary model name still returns and model says GPT-5.3-mini.
  - Maintainer said backend auto-routes models and frontend-passed model has limited effect.
- https://github.com/basketikun/chatgpt2api/issues/177
  - Maintainer said 5.5 appears in web model list, but passing it can still route to mini models.
- https://github.com/basketikun/chatgpt2api/issues/77
  - Maintainer said chat interface exists but UI lacked it; 5.5 planned around Pro accounts.
- https://github.com/basketikun/chatgpt2api/issues/291
  - Users asked about `gpt-5-5-pro` / `gpt-5-5-thinking`; results still felt like fast/standard routing.

PR search checked:

- GitHub API search for `gpt-5-3-mini is:pr`, `gpt-5-5 is:pr`, `model fallback is:pr`, `force_paragen_model_slug is:pr` found no matching PRs.

Current local code observations:

- Text conversation payload sends `"model": model` directly in `OpenAIBackendAPI._conversation_payload(...)`.
- Default chat model is often `auto` in API handlers/tests.
- `SEARCH_MODEL = "gpt-5-5"`, `CODEX_RESPONSES_MODEL = "gpt-5.5"`, and `EDITABLE_FILE_MODEL = "gpt-5-5-thinking"` exist, but they do not prove normal text chat can force 5.5.
- `force_paragen_model_slug` currently remains empty in text conversation payload.

Potential future work:

1. Add strict model validation: reject unknown model names instead of forwarding arbitrary `model` values.
2. Add config option such as `default_text_model = "gpt-5-5"` so API default stops using `auto`.
3. Experiment with `force_paragen_model_slug` / related web payload fields, but treat this as non-guaranteed because upstream issues indicate server-side auto-routing.
4. Add response diagnostics: record requested model, sent model, account type, `default_model_slug`, and model self-report text if present.
5. Add account capability probe that asks a controlled model-identification prompt and records whether the account is actually being routed to mini.

Status:

- Do not assume this can be fully forced from this repo.
- Best near-term fix is strict validation + default model preference + diagnostics.
