"""
LLM-assisted validation of user replies for onboarding: sidebar caption + quality.

Uses the same Groq/OpenAI-compatible client as the phase classifier when
GROQ_API_KEY is set; otherwise heuristics only.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

VALIDATION_SYSTEM = """You are validating a practice admin's chat reply during PrescriberPoint account setup.

Assess ONLY the user's last message relative to the assistant's last question (and the phase hint).

Return a single JSON object with keys:
- "quality": one of "ok", "weak", "nonsense"
  - ok: clear enough to record a setting (typos OK if intent is clear)
  - weak: vague, too short, or partially off-topic but might be salvageable with one follow-up
  - nonsense: gibberish, random characters, unrelated spam, empty of meaning, or clearly not answering the question
- "sidebar_label": short human-readable summary for a config sidebar (max 12 words, no quotes). Use empty string if quality is nonsense.
- "escalate_suggested": true if the user seems frustrated, mentions legal/compliance beyond self-serve, abusive language, or repeated inability to proceed; else false

Rules:
- Long but coherent answers are "ok" with a concise sidebar_label capturing the substance.
- Medical emergencies or urgent clinical questions: escalate_suggested true, quality weak or nonsense as appropriate.

Reply with ONLY the JSON object, no markdown."""

_bootstrap_needles = (
    "begin the configuration conversation",
    "the practice has confirmed their details",
)


def is_bootstrap_user_message(text: str) -> bool:
    t = text.strip().lower()
    if len(t) > 280:
        return any(n in t for n in _bootstrap_needles)
    return any(n in t for n in _bootstrap_needles)


_client: OpenAI | None = None
if settings.CLASSIFY_API_KEY:
    _client = OpenAI(
        api_key=settings.CLASSIFY_API_KEY,
        base_url=settings.CLASSIFY_BASE_URL,
    )


def _heuristic_nonsense(text: str) -> bool:
    t = text.strip()
    if len(t) < 2:
        return True
    letters = sum(c.isalpha() for c in t)
    if len(t) >= 8 and letters < len(t) * 0.25:
        return True
    if len(t.split()) <= 1 and letters < 3 and len(t) < 20:
        return False  # e.g. "Yes" / "No" — not nonsense
    return False


def _heuristic_validate(user_text: str) -> dict[str, Any]:
    t = user_text.strip()
    if _heuristic_nonsense(t):
        return {
            "quality": "nonsense",
            "sidebar_label": "",
            "escalate_suggested": False,
        }
    words = t.split()
    label = " ".join(words[:14])[:100]
    quality = "weak" if len(words) > 35 or len(t) > 400 else "ok"
    return {
        "quality": quality,
        "sidebar_label": label,
        "escalate_suggested": False,
    }


def _parse_validation_json(raw: str) -> dict[str, Any] | None:
    cleaned = _THINK_RE.sub("", raw).strip()
    try:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start < 0 or end <= start:
            return None
        data = json.loads(cleaned[start:end])
        if data.get("quality") not in ("ok", "weak", "nonsense"):
            return None
        data.setdefault("sidebar_label", "")
        data.setdefault("escalate_suggested", False)
        data["sidebar_label"] = str(data["sidebar_label"])[:120]
        return data
    except (json.JSONDecodeError, TypeError):
        return None


def validate_user_reply(
    *,
    user_text: str,
    last_assistant: str | None,
    phase_hint: str,
) -> dict[str, Any]:
    """
    Returns dict with keys: quality, sidebar_label, escalate_suggested (bool).
    """
    if _client:
        try:
            ctx = json.dumps(
                {
                    "phase_hint": phase_hint,
                    "last_assistant_question": (last_assistant or "")[:2000],
                    "user_reply": user_text[:4000],
                },
                ensure_ascii=False,
            )
            result = _client.chat.completions.create(
                model=settings.CLASSIFY_MODEL,
                messages=[
                    {"role": "system", "content": VALIDATION_SYSTEM},
                    {"role": "user", "content": ctx},
                ],
                max_tokens=256,
                temperature=0,
            )
            raw = result.choices[0].message.content or ""
            parsed = _parse_validation_json(raw)
            if parsed:
                return parsed
            logger.warning("Validation JSON parse failed, using heuristics")
        except Exception as e:
            logger.warning("Validation LLM failed: %s", e)

    return _heuristic_validate(user_text)


def heuristic_reply_quality(user_text: str) -> str:
    """ok | weak | nonsense — fast path without LLM."""
    return _heuristic_validate(user_text)["quality"]


def previous_user_message(messages: list[dict]) -> str | None:
    """User message before the last user message, if any."""
    seen_last_user = False
    for m in reversed(messages):
        if m["role"] != "user":
            continue
        if not seen_last_user:
            seen_last_user = True
            continue
        return m.get("content")
    return None
