# Product brief — PrescriberPoint AI practice onboarding (prototype)

**Audience:** Product, CS leadership, engineering reviewers (e.g. Ryan).  
**Companion:** This brief matches **current behavior in the repository** (`prescriberAI`). If Langfuse-hosted prompt text diverges from the code fallback, runtime behavior follows **Langfuse** when keys are set, else **`FALLBACK_PROMPT`** in `app/services/ai_service.py`.

---

## 1. Problem

New practices must configure PrescriberPoint before using drug lookup, prior authorization (PA), samples, and affordability tools. Today that setup consumes significant customer success time (on the order of **~2.3 contacts and ~45 minutes per practice** at assumed volume—see `README.md` for the working assumption). The **configuration conversation** is the universal gate: improving or automating it reduces linear scaling of CS load with signups.

## 2. Product goal (prototype)

Deliver a **credible end-to-end demo**: a practice admin enters an **NPI**, confirms registry data, completes an **AI-guided configuration chat** across **six fixed areas**, then sees a **summary**. The experience must support **escalation** to a human specialist when the practice’s needs exceed self-serve setup—without blocking the rest of the conversation.

**Non-goals for this prototype:** SSO, real account persistence, scheduling callbacks, billing, or production security/compliance hardening.

## 3. Primary user flow (as implemented)

| Step | UI state (`App.tsx`) | What happens |
|------|----------------------|--------------|
| 1 | NPI entry | User enters a **10-digit NPI**. Backend `GET /api/npi/{npi}` returns practice name, address, specialty, providers. **Live NPPES** is tried first; known **demo NPIs** use **mock data** if lookup fails or for offline demos (`app/services/npi_service.py`). |
| 2 | Confirm | User verifies **Yes, that’s us** or goes back. |
| 3 | Chat + sidebar | AI asks **one question per turn** (system rules). A **configuration sidebar** lists the six areas with **live phase** and **completed** rows; **completed rows are clickable** to send a **revise** message for that area (`frontend/src/components/Chat.tsx`, `ConfigSidebar.tsx`). |
| 4 | Summary | When the assistant’s reply contains the exact substring **`CONFIGURATION COMPLETE`** (case-insensitive), the client advances to the **summary** view with that text. |

**Progress bar:** Maps to coarse stages (identify / configure / done)—see `ProgressBar` + `STEP_INDEX` in `frontend/src/App.tsx`.

## 4. Configuration scope (six areas)

Order and semantics are fixed in code (`CONFIG_AREAS` in `app/services/ai_service.py`, labels in `frontend/src/types.ts`):

1. **Patient demographics** — Age groups served (pediatric, adult, geriatric).  
2. **Prescribing focus** — Drug categories, generics vs brand, therapeutic emphasis.  
3. **Prior auth** — Payers, submission preferences, workflow priorities.  
4. **Sample management** — Stocking samples, categories, dropship vs rep-delivered.  
5. **Coverage & affordability** — Patient assistance, copay cards, what to surface.  
6. **Provider roles** — Who may submit PAs, request samples, administer the account.

**Phase model:** Each chat turn runs a **classifier** (Groq **Qwen** when `GROQ_API_KEY` is set; otherwise **keyword fallback** on conversation text) to set `current_phase`, exposed in **`POST /api/chat`** as `current_phase`. The UI only marks a phase **completed** in the sidebar when the phase **moves forward** in this order and the user has provided a substantive reply (see `Chat.tsx` logic)—reducing false progress on bad answers.

## 5. Escalation (product + detection)

**Product intent:** Multi-site operations, EMR/EHR integration, custom API/data feeds, or uncertain compliance should trigger a **specialist handoff** while the assistant continues with areas it can still configure.

**Prompt instruction (fallback / Langfuse-aligned intent):** The model is instructed to include the phrase **`connect you with a PrescriberPoint specialist`** when those topics appear (`FALLBACK_PROMPT` in `ai_service.py`).

**API / UI signal:** `check_complete` sets `needs_escalation` if the assistant’s **last reply** contains any of the lowercase substrings in `ESCALATION_SIGNALS` (e.g. `connect you with a prescriberpoint specialist`, `beyond what i can configure`, …). The UI shows a **Specialist recommended** banner and a **Schedule Call** button (prototype stub: alert only).

## 6. Technical summary (aligned with repo)

| Layer | Implementation |
|--------|------------------|
| Frontend | React 19, TypeScript, Vite; dev server proxies `/api` to backend `:8080`. |
| Backend | FastAPI, Python 3.12+, `uv`; CORS for Vite origin. |
| Agent | **LangGraph:** `classify` → `respond` → `check_complete` per user message. |
| Response model | **Anthropic** via LangChain `ChatAnthropic`; model id from **`ANTHROPIC_MODEL`** env (default `claude-sonnet-4-20250514` in `app/config.py`). |
| Classifier | **Groq** OpenAI-compatible API, default model **`qwen/qwen3-32b`**; optional. |
| Prompts | Langfuse prompt **`onboarding-system-prompt`**, label **`production`**, if `LANGFUSE_PUBLIC_KEY` / secret / host set; else in-repo fallback string. |
| Observability | Langfuse **LangChain `CallbackHandler`** on graph runs when public key set; traces include session id from client (`session_id` on `ChatRequest`). |
| APIs | `GET /api/npi/{npi}`, `POST /api/chat` (body: `messages`, `practice_context`, optional `session_id`). Response: `response`, `current_phase`, `needs_escalation`. |

## 7. How we test (reviewer checklist)

- **Automated:** `uv run pytest tests/test_functional_e2e.py` — Scenario A (completion) and B (escalation) over HTTP with mocked Claude.  
- **Manual chat scripts:** `docs/e2e-scenarios.md` (suggested user messages for A and B).  
- **Diagrams:** `docs/architecture.mermaid`, `docs/user-flow.mermaid`.

## 8. Success criteria (observable)

- **A — Complete:** After a coherent dialogue through the six areas, assistant ends with **`CONFIGURATION COMPLETE`**; app shows **summary**.  
- **B — Escalate:** User describes e.g. **Epic / multi-site / EMR**; assistant uses specialist handoff language; **`needs_escalation`** true and **banner** visible.  
- **C — Identity:** NPI path returns consistent practice context for demo NPIs and live NPPES when available.

## 9. Document map

| Doc | Purpose |
|-----|---------|
| `README.md` | One-page overview, run commands, env summary. |
| `AGENTS.md` | Developer / agent orientation. |
| `docs/e2e-scenarios.md` | Manual + automated E2E detail. |
| `docs/product-brief.md` | This brief — product alignment with code. |
