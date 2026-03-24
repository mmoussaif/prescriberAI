# PrescriberPoint — AI Practice Onboarding (Prototype)

## What I Built

End-to-end wizard: **NPI lookup** (live NPPES + mock demo NPIs) → **confirm practice** → **AI-guided configuration** (6 areas: demographics, prescribing, prior auth, samples, coverage, provider roles) → **summary**. **React + Vite** frontend; **FastAPI** backend. **LangGraph** agent: classify → **validate** (reply quality + `sidebar_caption`) → respond → check_complete. **Qwen 3** (Groq) classifies phase and validates replies when `GROQ_API_KEY` is set; **Claude Sonnet** generates replies. **Langfuse** hosts the system prompt (`onboarding-system-prompt`, production label). **Sidebar** shows settings with intelligent captions; completed rows are **clickable to revise**. **Escalation** (multi-site / EMR, or repeated nonsense / validator suggestion) shows a specialist banner; chat continues for areas the AI can still configure.

## Why This Piece

~2.3 CS calls and ~45 min per practice → **~60 CS-hours/week** at current volume. Every practice hits configuration before PA, samples, or drug tools—this is where CS time concentrates. Proving AI can configure a standard practice from NPPES + conversation tests the core bet: break the linear link between signups and CS labor.

## Run Locally

```bash
uv sync && uv run uvicorn app.main:app --reload --port 8080 --env-file .env
cd frontend && npm i && npm run dev   # second terminal → http://localhost:5173  
# Optional: `frontend/.env` → `VITE_SPECIALIST_PHONE=+15551234567` for Schedule Walkthrough `tel:` on the summary (escalation uses built-in Call +17743579384)
```

**Demo NPIs:** `1234567890` · `9876543210` · `5551234567` (mock if NPPES misses).

**Env:** Copy `.env.example` → `.env`. **Required:** `ANTHROPIC_API_KEY`. **Optional:** `ANTHROPIC_MODEL`, `GROQ_API_KEY` (phase classify + reply validate; else keyword + heuristics), `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` (prompts + observability).

**Tests:** `uv run pytest tests/ -v` (optional live-LLM chat cases in `tests/test_api_e2e.py` skip without `ANTHROPIC_API_KEY`). **Functional E2E** (NPI + chat, completion vs escalation, mocked Claude): `tests/test_functional_e2e.py` — see [`docs/e2e-scenarios.md`](docs/e2e-scenarios.md) (**Manual QA** = what to type in chat for Scenario A & B). **Agent/dev guide:** [`AGENTS.md`](AGENTS.md).

## What I’d Do Next

1. Shadow 20 onboardings—AI vs CS config match rate.  
2. Guided first real workflow (e.g. one PA) post-setup—activation, not just setup.  
3. Instrument **first real workflow within 48h**, not completion rate alone.

## Tools

FastAPI · uv · LangGraph · Claude (Anthropic) · Qwen/Groq · Langfuse · NPPES · React/TS/Vite · pytest · Docker

**Product brief (aligned with shipped behavior):** [`docs/product-brief.md`](docs/product-brief.md)

**Diagrams:** `docs/architecture.mermaid`, `docs/user-flow.mermaid`.
