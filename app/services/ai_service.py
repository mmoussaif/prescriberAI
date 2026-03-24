"""
AI onboarding agent built with LangGraph.

Graph: START → classify → respond → check_complete → END
  - classify:        Determines which config area we're in based on conversation
  - respond:         Generates the next AI response with phase-aware prompting
  - check_complete:  Detects if configuration is done or needs escalation

Langfuse traces every invocation for observability.
"""

from __future__ import annotations

import json
import logging
from typing import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from openai import OpenAI

from app.config import settings
from app.models.schemas import PracticeInfo, ChatMessage

logger = logging.getLogger(__name__)

PROMPT_NAME = "onboarding-system-prompt"


# ---------------------------------------------------------------------------
# Langfuse (optional — gracefully degrades if not configured)
# ---------------------------------------------------------------------------

def _get_langfuse_client():
    """Return a Langfuse client, or None if not configured."""
    if not settings.LANGFUSE_PUBLIC_KEY:
        return None
    try:
        from langfuse import Langfuse
        return Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
    except Exception as e:
        logger.warning("Langfuse client not available: %s", e)
        return None


_langfuse = _get_langfuse_client()


# ---------------------------------------------------------------------------
# Prompt — fetched from Langfuse (with hardcoded fallback)
# ---------------------------------------------------------------------------

FALLBACK_PROMPT = """\
You are an AI onboarding assistant for PrescriberPoint, an AI-powered prescribing \
platform that helps healthcare providers get patients on therapy faster. The platform offers drug \
information lookup (35K+ FDA-approved labels), prior authorization tools, drug sample ordering \
(dropship and rep-delivered), and coverage/affordability resources.

You are helping a new practice configure their PrescriberPoint account.

PRACTICE CONTEXT:
{{practice_context}}

CURRENT CONFIGURATION PHASE: {{current_phase}}

CONFIGURATION AREAS (cover in this order):
1. patient_demographics — Age groups served (pediatric, adult, geriatric)
2. prescribing_focus — Common drug categories, generics vs brand preference
3. prior_auth — Top payers, auto-submission preferences, workflow priorities
4. sample_management — Whether they stock samples, categories, dropship vs rep-delivered
5. coverage_affordability — Patient assistance programs and copay cards to surface
6. provider_roles — Who can submit PAs, request samples, manage the account

RULES:
- 2-4 sentences max per turn. Be concise and warm.
- Ask ONE focused question at a time
- Use healthcare terminology naturally
- If admin is uncertain, offer a default: "Most [specialty] practices do X — want me to set that?"
- Never re-ask information already in the practice context
- When all areas are covered, output a summary starting with exactly "CONFIGURATION COMPLETE"

ESCALATION — if the admin mentions any of these, acknowledge it and include the phrase \
"connect you with a PrescriberPoint specialist" in your response:
- Multiple locations or shared provider rosters across sites
- EMR/EHR integration requirements (Epic, Cerner, etc.)
- Custom API or data feed needs
- Compliance or regulatory constraints you're unsure about
Continue configuring the areas you CAN handle; the specialist handles the rest.

TONE: Competent, efficient, human. Like a knowledgeable colleague who understands prescribing workflows."""


def _compile_system_prompt(practice_context: str, current_phase: str) -> str:
    """Fetch prompt from Langfuse and compile, falling back to hardcoded version."""
    if _langfuse:
        try:
            prompt = _langfuse.get_prompt(PROMPT_NAME, label="production")
            return prompt.compile(
                practice_context=practice_context,
                current_phase=current_phase,
            )
        except Exception as e:
            logger.warning("Failed to fetch prompt from Langfuse, using fallback: %s", e)

    return FALLBACK_PROMPT.replace(
        "{{practice_context}}", practice_context
    ).replace(
        "{{current_phase}}", current_phase
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

CONFIG_AREAS = [
    "patient_demographics",
    "prescribing_focus",
    "prior_auth",
    "sample_management",
    "coverage_affordability",
    "provider_roles",
]


class OnboardingState(TypedDict):
    messages: list[dict]
    practice_context: dict
    current_phase: str
    is_complete: bool
    needs_escalation: bool
    response: str


# ---------------------------------------------------------------------------
# Classifier — LLM-based (Qwen via Groq) with keyword fallback
# ---------------------------------------------------------------------------

CLASSIFY_SYSTEM = """\
You are a classifier. Given a conversation between an AI assistant and a practice admin, \
return which configuration area needs to be addressed NEXT.

Areas (in order):
1. patient_demographics
2. prescribing_focus
3. prior_auth
4. sample_management
5. coverage_affordability
6. provider_roles

An area is ONLY covered if the admin gave a clear, substantive answer about it. \
These do NOT count as covered: gibberish, typos, "I don't know", off-topic text, \
or the AI asking a question. Only a real answer from the admin counts.

Return the FIRST uncovered area key, or "summary" if all 6 are covered.
Reply with ONLY the key, no explanation."""

_classify_client: OpenAI | None = None
if settings.CLASSIFY_API_KEY:
    _classify_client = OpenAI(
        api_key=settings.CLASSIFY_API_KEY,
        base_url=settings.CLASSIFY_BASE_URL,
    )


import re

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _classify_with_llm(messages: list[dict]) -> str | None:
    """Use Qwen via Groq to classify the current phase."""
    if not _classify_client:
        return None
    try:
        conversation = "\n".join(
            f"{'ADMIN' if m['role'] == 'user' else 'AI'}: {m['content']}"
            for m in messages
        )
        result = _classify_client.chat.completions.create(
            model=settings.CLASSIFY_MODEL,
            messages=[
                {"role": "system", "content": CLASSIFY_SYSTEM},
                {"role": "user", "content": conversation},
            ],
            max_tokens=512,
            temperature=0,
        )
        raw = result.choices[0].message.content or ""
        cleaned = _THINK_RE.sub("", raw).strip().lower()
        if cleaned in CONFIG_AREAS or cleaned == "summary":
            return cleaned
        for area in CONFIG_AREAS:
            if area in cleaned:
                return area
        if "summary" in cleaned:
            return "summary"
        logger.warning("LLM classifier returned unexpected value: %s", cleaned[:100])
        return None
    except Exception as e:
        logger.warning("LLM classifier failed, falling back to keywords: %s", e)
        return None


def _classify_with_keywords(messages: list[dict]) -> str:
    """Fallback keyword-based classifier."""
    conversation_text = " ".join(m["content"] for m in messages).lower()
    area_keywords = {
        "patient_demographics": ["age group", "pediatric through", "geriatric patient", "adults only"],
        "prescribing_focus": ["drug categor", "generics first", "brand name", "therapeutic area"],
        "prior_auth": ["payer", "insurance", "prior auth", "auto-submit"],
        "sample_management": ["sample", "dropship", "rep-deliver"],
        "coverage_affordability": ["copay card", "patient assistance", "affordability program"],
        "provider_roles": ["account admin", "who can submit", "permissions for"],
    }
    for area in CONFIG_AREAS:
        keywords = area_keywords[area]
        if not any(kw in conversation_text for kw in keywords):
            return area
    return "summary"


def classify_phase(state: OnboardingState) -> OnboardingState:
    """Determine which configuration area the conversation is currently in."""
    phase = _classify_with_llm(state["messages"])
    if phase is None:
        phase = _classify_with_keywords(state["messages"])
    state["current_phase"] = phase
    return state


def respond(state: OnboardingState) -> OnboardingState:
    """Generate the AI response using ChatAnthropic."""
    llm = ChatAnthropic(
        model=settings.ANTHROPIC_MODEL,
        api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=1024,
    )

    system = _compile_system_prompt(
        practice_context=json.dumps(state["practice_context"], indent=2),
        current_phase=state["current_phase"],
    )

    lc_messages = [SystemMessage(content=system)]
    for m in state["messages"]:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            lc_messages.append(AIMessage(content=m["content"]))

    result = llm.invoke(lc_messages)
    state["response"] = result.content
    return state


ESCALATION_SIGNALS = [
    "connect you with a specialist",
    "connect you with a prescriberpoint specialist",
    "i want to make sure i get this right",
    "beyond what i can configure",
    "needs hands-on setup",
    "recommend speaking with",
]


def check_complete(state: OnboardingState) -> OnboardingState:
    """Check if the configuration is complete or needs escalation."""
    response_upper = state["response"].upper()
    response_lower = state["response"].lower()
    state["is_complete"] = "CONFIGURATION COMPLETE" in response_upper
    state["needs_escalation"] = any(s in response_lower for s in ESCALATION_SIGNALS)
    return state


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_onboarding_graph() -> StateGraph:
    graph = StateGraph(OnboardingState)

    graph.add_node("classify", classify_phase)
    graph.add_node("respond", respond)
    graph.add_node("check_complete", check_complete)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "respond")
    graph.add_edge("respond", "check_complete")
    graph.add_edge("check_complete", END)

    return graph.compile()


# Compile once at module level
onboarding_agent = build_onboarding_graph()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_ai_response(
    messages: list[ChatMessage], practice_context: PracticeInfo
) -> dict:
    """Run one turn of the onboarding agent and return response + metadata.

    Traced by Langfuse when LANGFUSE_PUBLIC_KEY is set (via OpenTelemetry in v4).
    """

    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    state: OnboardingState = {
        "messages": [{"role": m.role, "content": m.content} for m in messages],
        "practice_context": practice_context.model_dump(),
        "current_phase": "patient_demographics",
        "is_complete": False,
        "needs_escalation": False,
        "response": "",
    }

    result = onboarding_agent.invoke(state)
    return {
        "response": result["response"],
        "current_phase": result["current_phase"],
        "needs_escalation": result["needs_escalation"],
    }
