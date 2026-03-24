# Test suite

Python tests for the **FastAPI** backend (`pytest`). The **React** app has no automated tests in this repo; exercise it manually per [`docs/e2e-scenarios.md`](../docs/e2e-scenarios.md).

## Quick commands

```bash
# Full suite (recommended before push)
uv run pytest tests/ -v

# Only HTTP journey tests (mocked Claude, no real API keys)
uv run pytest tests/test_functional_e2e.py -v
uv run pytest tests/ -m e2e -v
```

## What each module covers

| File | Purpose |
|------|---------|
| `conftest.py` | Shared `TestClient` fixture; `e2e_llm_mocks` forces a dummy `ANTHROPIC_API_KEY`, clears Langfuse keys, and nulls the Langfuse client so graph runs use the in-repo fallback prompt. |
| `test_functional_e2e.py` | **Scenario A / B** — full `GET /api/npi` + `POST /api/chat` flows with **`ChatAnthropic` mocked**. Asserts `CONFIGURATION COMPLETE` vs `needs_escalation`. Documented step-by-step in [`docs/e2e-scenarios.md`](../docs/e2e-scenarios.md). |
| `test_api_e2e.py` | Route-level checks: NPI validation and shapes; **optional** live Anthropic chat cases when `ANTHROPIC_API_KEY` is set (skipped otherwise). |
| `test_onboarding_validation.py` | Reply validation helpers: bootstrap detection, heuristic quality, JSON shape when Groq client is absent. |
| `test_classify.py` | Keyword phase classifier, `check_complete`, escalation substring list, Qwen think-tag stripping. |
| `test_schemas.py` | Pydantic `ChatRequest` / `ChatResponse` (including `sidebar_caption`, `validation_quality`). |
| `test_npi_service.py` | Mock NPPES data and lookup helpers. |

## Notes

- **Groq / Qwen** is not mocked in functional E2E; with `GROQ_API_KEY` unset (typical in CI), phase classification and reply validation use **keyword / heuristic** paths, so tests stay deterministic.
- **LangGraph** runs for every chat test; invocation counts on mocks assume the current graph (`classify` → `validate` → `respond` → `check_complete`).
