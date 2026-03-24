"""E2E tests for the FastAPI endpoints.

These tests use FastAPI's TestClient and hit the real API routes.
NPI tests use mock data (no network). Chat tests are skipped if
ANTHROPIC_API_KEY is not set (to avoid CI failures without secrets).
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MOCK_NPI = "1234567890"
REAL_PRACTICE = {
    "npi": "1234567890",
    "practice_name": "Springfield Family Medicine",
    "address": "742 Evergreen Terrace, Springfield, IL 62704",
    "specialty": "Family Medicine",
}

has_anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))


class TestNpiEndpoint:
    def test_valid_mock_npi(self):
        resp = client.get(f"/api/npi/{MOCK_NPI}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["practice_name"] == REAL_PRACTICE["practice_name"]
        assert data["specialty"] == REAL_PRACTICE["specialty"]
        assert len(data["providers"]) == 3

    def test_invalid_npi_format(self):
        resp = client.get("/api/npi/123")
        assert resp.status_code == 400
        assert "10-digit" in resp.json()["detail"]

    def test_non_numeric_npi(self):
        resp = client.get("/api/npi/abcdefghij")
        assert resp.status_code == 400

    def test_unknown_npi_returns_404(self):
        resp = client.get("/api/npi/0000000000")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_npi_response_shape(self):
        resp = client.get(f"/api/npi/{MOCK_NPI}")
        data = resp.json()
        assert "npi" in data
        assert "practice_name" in data
        assert "address" in data
        assert "specialty" in data
        assert "providers" in data
        assert isinstance(data["providers"], list)
        for p in data["providers"]:
            assert "name" in p
            assert "role" in p
            assert "npi" in p


class TestChatEndpoint:
    @pytest.mark.skipif(not has_anthropic_key, reason="ANTHROPIC_API_KEY not set")
    def test_first_turn_returns_greeting(self):
        resp = client.post(
            "/api/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Begin the configuration conversation."}
                ],
                "practice_context": {
                    "npi": MOCK_NPI,
                    "practice_name": "Springfield Family Medicine",
                    "address": "742 Evergreen Terrace, Springfield, IL 62704",
                    "specialty": "Family Medicine",
                    "providers": [
                        {"name": "Dr. Sarah Chen", "role": "Physician", "npi": MOCK_NPI}
                    ],
                },
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert "current_phase" in data
        assert "needs_escalation" in data
        assert len(data["response"]) > 20

    @pytest.mark.skipif(not has_anthropic_key, reason="ANTHROPIC_API_KEY not set")
    def test_gibberish_stays_on_same_phase(self):
        resp = client.post(
            "/api/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Begin."},
                    {"role": "assistant", "content": "What age groups do you serve?"},
                    {"role": "user", "content": "asdfghjkl"},
                ],
                "practice_context": {
                    "npi": MOCK_NPI,
                    "practice_name": "Test",
                    "address": "123 Main",
                    "specialty": "Family Medicine",
                    "providers": [],
                },
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_phase"] == "patient_demographics"

    @pytest.mark.skipif(not has_anthropic_key, reason="ANTHROPIC_API_KEY not set")
    def test_real_answer_advances_phase(self):
        resp = client.post(
            "/api/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Begin."},
                    {"role": "assistant", "content": "What age groups do you serve?"},
                    {"role": "user", "content": "Mostly adults, some geriatric. No pediatrics."},
                ],
                "practice_context": {
                    "npi": MOCK_NPI,
                    "practice_name": "Test",
                    "address": "123 Main",
                    "specialty": "Family Medicine",
                    "providers": [],
                },
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_phase"] in ("prescribing_focus", "prior_auth")

    def test_missing_api_key_returns_500(self):
        original = os.environ.get("ANTHROPIC_API_KEY", "")
        try:
            os.environ["ANTHROPIC_API_KEY"] = ""
            from app.config import settings
            settings.ANTHROPIC_API_KEY = ""
            resp = client.post(
                "/api/chat",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "practice_context": {
                        "npi": "1234567890",
                        "practice_name": "Test",
                        "address": "123",
                        "specialty": "FM",
                        "providers": [],
                    },
                },
            )
            assert resp.status_code == 500
        finally:
            os.environ["ANTHROPIC_API_KEY"] = original
            settings.ANTHROPIC_API_KEY = original

    def test_invalid_request_body(self):
        resp = client.post("/api/chat", json={"bad": "data"})
        assert resp.status_code == 422
