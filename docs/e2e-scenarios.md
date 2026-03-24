# E2E functional scenarios

This doc covers **automated** tests (pytest) and **manual** browser QA: what to send in chat so testers can run **Scenario A** (finish onboarding) and **Scenario B** (escalation) predictably.

Stakeholder-facing product summary (kept in sync with the app): [`product-brief.md`](product-brief.md).

---

## Manual QA — what to type in chat

**Setup**

- Run backend + frontend (`AGENTS.md`).
- Open `http://localhost:5173`. The **Dashboard** lists practices saved in this browser (after a completed run). Click **Configure a practice** (or **Start onboarding** if the list is empty), then use demo NPI **`1234567890`** (mock practice) or any valid flow to **Confirm** and enter chat.
- During the wizard, **Dashboard** in the header returns to the saved-practice grid without losing stored summaries.

**How the assistant behaves**

- It asks **one question at a time**. Reply **after each assistant message** (don’t paste the whole script in one message unless you’re debugging).
- The app tracks **six areas** in order: Patient Demographics → Prescribing Focus → Prior Auth → Samples → Coverage & Affordability → Provider Roles. Your answers should **substantively address** what it asked; vague or off-topic replies may keep you on the same topic.
- **Success (A):** the assistant eventually returns a block that includes the exact phrase **`CONFIGURATION COMPLETE`**; the UI moves to the **summary** step.
- **Success (B):** the assistant mentions connecting you with a **PrescriberPoint specialist** (or similar escalation copy); the **Specialist recommended** banner appears and `needs_escalation` is true in the API.

---

### Scenario A — Configuration complete (happy path)

Goal: complete all configuration areas so the model closes with **`CONFIGURATION COMPLETE`**.

Use the **suggested replies** below when the assistant’s question matches that **topic**. If the wording differs slightly, answer in the same spirit and **include the keywords in parentheses** so phase detection stays reliable (especially if `GROQ_API_KEY` is unset and the app uses keyword fallback).

| # | Topic (sidebar) | When you see the AI asking about… | Suggested reply (copy or adapt) |
|---|-------------------|-----------------------------------|----------------------------------|
| 1 | Patient Demographics | Age groups, pediatrics, who you treat | *“We see **adults** and **geriatric** patients; **no pediatrics**.”* |
| 2 | Prescribing Focus | Drug types, generics vs brand, therapeutic areas | *“Mostly **generics first**; we also use **brand name** drugs in cardiology and diabetes **therapeutic areas**.”* |
| 3 | Prior Authorization | Payers, insurance, PA workflow | *“Top **payers** are Aetna and UHC; we want **prior auth** tracked and **auto-submit** where possible.”* |
| 4 | Sample Management | Samples, rep, dropship | *“We keep some **samples** on site; prefer **rep-deliver**ed restocks and occasional **dropship**.”* |
| 5 | Coverage & Affordability | Copay cards, patient assistance | *“Show **copay cards** and **patient assistance** programs; we care about **affordability** for high-cost meds.”* |
| 6 | Provider Roles | Who submits PAs, admins the account | *“**Account admin** is the office manager; physicians are **who can submit** **prior auth**; define **permissions for** nurses to request **samples**.”* |

After area 6, if the assistant asks a final follow-up, answer briefly, then it should summarize with **`CONFIGURATION COMPLETE`**.

**If you get stuck**

- Reply with a **clear, concrete** sentence on the topic it asked about (avoid “I don’t know” or gibberish).
- If the same question repeats, restate your answer using the **bold keywords** from the table row for the current topic.
- Optional: set **`GROQ_API_KEY`** so the LLM classifier (Qwen) is used instead of keyword-only fallback (`app/services/ai_service.py`).

---

### Scenario B — Escalation (specialist handoff)

Goal: trigger **escalation** without needing to finish all six areas.

Send **one** user message (after the first assistant turn is fine) that clearly raises a **complex setup** the product prompt tells the model to escalate, for example:

**Example A (multi-site + EMR):**

> *“We use **Epic** across **three clinic sites** and need **deep EMR integration** for **prior auth** — not just the standard setup.”*

**Example B (multi-location roster):**

> *“We have **multiple locations** with a **shared provider roster** and need help syncing accounts.”*

**Example C (short):**

> *“We need **EHR integration** with **Cerner** and **API** access — this is beyond a normal solo practice setup.”*

**Pass criteria**

- Assistant response includes language about connecting you with a **PrescriberPoint specialist** (or equivalent escalation phrase defined in the system prompt).
- UI: **Specialist recommended** banner with **Call +17743579384** (prototype).

Escalation can appear **together with** normal configuration questions; the banner should still show when the model uses the handoff phrase.

---

## Automated tests (pytest)

Coverage lives in `tests/test_functional_e2e.py`. Those tests call the **same HTTP API** as the UI (`GET /api/npi/{npi}`, `POST /api/chat`) via FastAPI’s `TestClient` (in-process, no browser). **Claude is mocked** so CI does not need `ANTHROPIC_API_KEY`.

### Why two scenarios in automation

1. **Happy path** — response eventually contains `CONFIGURATION COMPLETE`; `needs_escalation` false.
2. **Escalation path** — response matches escalation detection; `needs_escalation` true.

### Scenario A — automated

| Step | Action | Assert |
|------|--------|--------|
| 1 | `GET /api/npi/1234567890` | 200 + mock practice |
| 2 | `POST /api/chat` — first wizard turn | 200, no `CONFIGURATION COMPLETE`, `needs_escalation` false |
| 3 | `POST /api/chat` — second turn | 200, `CONFIGURATION COMPLETE` in body, `needs_escalation` false |

### Scenario B — automated

| Step | Action | Assert |
|------|--------|--------|
| 1 | `GET /api/npi/1234567890` | 200 |
| 2 | `POST /api/chat` — user message (Epic / multi-site) | 200, `needs_escalation` true, specialist wording |

**Covered:** NPI + chat routers, schemas, LangGraph + `check_complete`, `session_id` on requests.

### What automation does not cover

- **Real browser/UI** — no Playwright/Cypress in repo; use the **Manual QA** section above.
- **Real Anthropic / Groq** — optional live checks in `tests/test_api_e2e.py` when `ANTHROPIC_API_KEY` is set.

### Running automated scenarios

```bash
uv run pytest tests/test_functional_e2e.py -v
uv run pytest tests/ -m e2e -v
```
