# PrescriberPoint — AI Practice Onboarding (Prototype)

## What I Built

End-to-end wizard: **NPI lookup** (live NPPES + mock demo NPIs) → **confirm practice** → **AI-guided configuration** (6 areas: demographics, prescribing, prior auth, samples, coverage, provider roles) → **summary**. **React + Vite** frontend; **FastAPI** backend. **LangGraph** agent: classify → respond → check_complete. **Qwen 3** (Groq, free tier) classifies which phase the conversation is in; **Claude Sonnet** generates replies. **Langfuse** hosts the system prompt (`onboarding-system-prompt`, production label). **Sidebar** shows settings as they’re set; completed rows are **clickable to revise**. **Escalation** (multi-site / EMR) shows a specialist banner; chat continues for areas the AI can still configure.

## Why This Piece

~2.3 CS calls and ~45 min per practice → **~60 CS-hours/week** at current volume. Every practice hits configuration before PA, samples, or drug tools—this is where CS time concentrates. Proving AI can configure a standard practice from NPPES + conversation tests the core bet: break the linear link between signups and CS labor.

## Run Locally

```bash
uv sync && uv run uvicorn app.main:app --reload --port 8080 --env-file .env
cd frontend && npm i && npm run dev   # second terminal → http://localhost:5173
```

**Demo NPIs:** `1234567890` · `9876543210` · `5551234567` (mock if NPPES misses).

**Env:** Copy `.env.example` → `.env`. **Required:** `ANTHROPIC_API_KEY`. **Optional:** `GROQ_API_KEY` (classifier; else keyword fallback), `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` (prompts + observability).

**Tests:** `uv run pytest tests/ -v` (chat tests skip if `ANTHROPIC_API_KEY` unset).

## What I’d Do Next

1. Shadow 20 onboardings—AI vs CS config match rate.  
2. Guided first real workflow (e.g. one PA) post-setup—activation, not just setup.  
3. Instrument **first real workflow within 48h**, not completion rate alone.

## Tools

FastAPI · uv · LangGraph · Claude (Anthropic) · Qwen/Groq · Langfuse · NPPES · React/TS/Vite · pytest · Docker

**Diagrams:** `docs/architecture.mermaid`, `docs/user-flow.mermaid`.
