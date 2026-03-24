"""Shared pytest fixtures for the FastAPI app.

`api_client` — FastAPI TestClient bound to `app.main:app`.

`e2e_llm_mocks` — Use on chat E2E tests: sets a dummy Anthropic key, clears Langfuse
env on `settings`, and sets `ai_service._langfuse` to None so the graph uses
`FALLBACK_PROMPT`. Does not set `GROQ_API_KEY`, so classify + validate use
keyword/heuristic paths (deterministic in CI).
"""

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import ai_service


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def e2e_llm_mocks(monkeypatch: pytest.MonkeyPatch):
    """Mock-friendly chat environment: dummy Anthropic key, Langfuse disabled."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api-dummy-e2e")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant-api-dummy-e2e", raising=False)
    monkeypatch.setattr(settings, "LANGFUSE_PUBLIC_KEY", "", raising=False)
    monkeypatch.setattr(settings, "LANGFUSE_SECRET_KEY", "", raising=False)
    monkeypatch.setattr(ai_service, "_langfuse", None)
