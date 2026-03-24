# Agent / developer guide

Quick orientation for humans and coding agents working on this repository.

## What this is

PrescriberPoint **AI practice onboarding** prototype: NPI lookup → practice confirm → conversational configuration (six areas) → summary. Backend is **FastAPI**; frontend is **React + Vite + TypeScript**. The agent is a **LangGraph** graph (`classify` → `validate` → `respond` → `check_complete`) in `app/services/ai_service.py` with `app/services/onboarding_validation.py` for reply quality and `sidebar_caption`.

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8080 --env-file .env
cd frontend && npm install && npm run dev
```

Open `http://localhost:5173`. API is proxied to `:8080`.

Optional: `frontend/.env` with `VITE_SPECIALIST_PHONE=+1…` so **Schedule Walkthrough** on the summary uses a **`tel:`** link (see `frontend/.env.example`). The escalation banner uses **Call +17743579384** with `tel:` built in. Restart `npm run dev` after changing env. Without a number on the summary, that button toggles **inline setup instructions**. Test `tel:` in a normal desktop/mobile browser if the IDE browser does nothing.

## Tests

| Suite | Command | Notes |
|-------|---------|--------|
| All | `uv run pytest tests/ -v` | |
| E2E scenarios (mocked LLM) | `uv run pytest tests/test_functional_e2e.py -v` or `pytest -m e2e` | **Scenario A/B** automated; **manual browser scripts** (what to type in chat) are in `docs/e2e-scenarios.md` → *Manual QA*. |
| API + live LLM (optional) | Same, with `ANTHROPIC_API_KEY` set | `tests/test_api_e2e.py` chat cases run; skipped without key. |

Functional E2E tests use **HTTP** against the app (`TestClient`); they do not drive the browser. They intentionally mock `ChatAnthropic` so CI stays deterministic.

## Environment

Copy `.env.example` → `.env`. Minimum for real chat: `ANTHROPIC_API_KEY`. Optional: `ANTHROPIC_MODEL` (defaults to `claude-sonnet-4-20250514`), `GROQ_API_KEY` (phase classifier), `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` (US: `https://us.cloud.langfuse.com`).

## Key files

| Path | Role |
|------|------|
| `docs/product-brief.md` | Product brief aligned with current code (send to stakeholders with the repo) |
| `app/services/ai_service.py` | LangGraph agent, Langfuse prompt fetch, escalation strings, Langfuse LangChain callback for traces |
| `app/routers/chat.py` | `POST /api/chat` |
| `app/routers/npi.py` | `GET /api/npi/{npi}` |
| `app/models/schemas.py` | Pydantic models (`ChatRequest.session_id`, etc.) |
| `frontend/src/components/Chat.tsx` | Chat UI, sidebar, escalation banner |
| `docs/e2e-scenarios.md` | **Documentation for the two automated E2E scenarios** |

## Conventions

- Python deps: `pyproject.toml` + `uv sync`.
- Frontend deps: `frontend/package.json`.
- Cursor rules: `.cursor/rules/` (`project.mdc`, `backend.mdc`, `frontend.mdc`).
