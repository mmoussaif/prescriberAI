"""Shared pytest fixtures."""

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
    """Chat tests with mocked Claude: dummy Anthropic key, no Langfuse prompt fetch."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api-dummy-e2e")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant-api-dummy-e2e", raising=False)
    monkeypatch.setattr(settings, "LANGFUSE_PUBLIC_KEY", "", raising=False)
    monkeypatch.setattr(settings, "LANGFUSE_SECRET_KEY", "", raising=False)
    monkeypatch.setattr(ai_service, "_langfuse", None)
