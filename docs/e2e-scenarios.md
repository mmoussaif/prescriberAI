# E2E functional scenarios

Automated coverage lives in `tests/test_functional_e2e.py`. Those tests call the **same HTTP API** the React app uses (`GET /api/npi/{npi}`, `POST /api/chat`) via FastAPI’s `TestClient` (in-process, no manual browser).

## Why two scenarios

The product has two critical outcomes after NPI confirmation:

1. **Happy path** — configuration finishes and the assistant emits a closing summary marked with `CONFIGURATION COMPLETE` (the UI then moves to the summary step).
2. **Escalation path** — the assistant acknowledges complexity (e.g. multi-site EMR) and includes the specialist handoff phrase so the API sets `needs_escalation: true` (the UI shows the escalation banner).

Other tests (`tests/test_api_e2e.py`, `tests/test_classify.py`, etc.) cover pieces of this; the functional E2E file strings **NPI + chat** together so regressions in routing, schemas, or graph wiring show up in one place.

## Scenario A — Configuration complete

| Step | Action | What we assert |
|------|--------|----------------|
| 1 | `GET /api/npi/1234567890` | 200 + mock practice payload (same as demo NPI in the app). |
| 2 | `POST /api/chat` — first wizard turn | 200, response has no `CONFIGURATION COMPLETE`, `needs_escalation` false. |
| 3 | `POST /api/chat` — second turn with prior assistant message in history | 200, response contains `CONFIGURATION COMPLETE`, `needs_escalation` false. |

**Claude** is **mocked** (`ChatAnthropic.invoke`) so CI does not need `ANTHROPIC_API_KEY`. The real **classify → respond → check_complete** LangGraph still runs; only the generative model output is fixed.

**Covered:** NPI router, chat router, Pydantic request/response shapes, `check_complete` completion detection, session id passthrough on the wire.

## Scenario B — Escalation

| Step | Action | What we assert |
|------|--------|----------------|
| 1 | `GET /api/npi/1234567890` | 200 + practice JSON reused as `practice_context`. |
| 2 | `POST /api/chat` — user message mentions Epic / multi-site EMR | 200, `needs_escalation` true, response mentions PrescriberPoint specialist (matches `ESCALATION_SIGNALS` in `app/services/ai_service.py`). |

**Claude** is mocked to return copy that includes the canonical escalation phrase.

**Covered:** Escalation detection in `check_complete`, chat payload with `session_id`, same stack as Scenario A.

## What is not covered here

- **Browser/UI** — not automated in this repo (no Playwright/Cypress). The functional tests validate the **backend contract** the UI depends on.
- **Real Anthropic / Groq** — optional live tests remain in `tests/test_api_e2e.py` when `ANTHROPIC_API_KEY` is set.
- **Langfuse export** — the E2E fixture clears Langfuse prompt client for isolation; tracing is tested indirectly only when running the app with keys.

## Running the scenarios

```bash
uv run pytest tests/test_functional_e2e.py -v
# or only marked e2e tests:
uv run pytest tests/ -m e2e -v
```
