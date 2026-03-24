"""Full functional E2E journeys over HTTP (FastAPI TestClient).

Exercises the same routes the React app uses: ``GET /api/npi/{npi}`` and
``POST /api/chat``. **Claude** (``ChatAnthropic``) is mocked so CI needs no
``ANTHROPIC_API_KEY``. The LangGraph pipeline still runs **classify → validate →
respond → check_complete**; with **Groq** unset, validate uses heuristics.

Scenario tables and manual scripts: ``docs/e2e-scenarios.md``.
Test index: ``tests/README.md``.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

MOCK_NPI = "1234567890"


@pytest.mark.e2e
class TestFunctionalE2EConfigurationComplete:
    """E2E Scenario A — wizard completes (summary / CONFIGURATION COMPLETE)."""

    def test_npi_then_chat_finishes_with_configuration_complete(
        self, api_client, e2e_llm_mocks
    ):
        npi_resp = api_client.get(f"/api/npi/{MOCK_NPI}")
        assert npi_resp.status_code == 200
        practice = npi_resp.json()
        assert practice["practice_name"]
        assert practice["npi"] == MOCK_NPI

        turn1_content = (
            "Welcome to PrescriberPoint! Let's start with patient demographics — "
            "which age groups does your practice primarily serve?"
        )
        turn2_content = (
            "CONFIGURATION COMPLETE\n\n"
            "Here is your setup summary: demographics, prescribing, PA workflow, "
            "samples, coverage tools, and provider roles are configured."
        )

        with patch("app.services.ai_service.ChatAnthropic") as mock_llm_cls:
            instance = MagicMock()
            mock_llm_cls.return_value = instance
            instance.invoke.side_effect = [
                MagicMock(content=turn1_content),
                MagicMock(content=turn2_content),
            ]

            r1 = api_client.post(
                "/api/chat",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "The practice has confirmed their details. "
                                "Begin the configuration conversation."
                            ),
                        },
                    ],
                    "practice_context": practice,
                    "session_id": "e2e-complete",
                },
            )
            assert r1.status_code == 200
            d1 = r1.json()
            assert "response" in d1
            assert "CONFIGURATION COMPLETE" not in d1["response"].upper()
            assert d1.get("needs_escalation") is False

            r2 = api_client.post(
                "/api/chat",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "The practice has confirmed their details. "
                                "Begin the configuration conversation."
                            ),
                        },
                        {"role": "assistant", "content": d1["response"]},
                        {
                            "role": "user",
                            "content": (
                                "We're all set on every area — please give the final summary."
                            ),
                        },
                    ],
                    "practice_context": practice,
                    "session_id": "e2e-complete",
                },
            )
            assert r2.status_code == 200
            d2 = r2.json()
            assert "CONFIGURATION COMPLETE" in d2["response"].upper()
            assert d2.get("needs_escalation") is False

        assert instance.invoke.call_count == 2


@pytest.mark.e2e
class TestFunctionalE2EEscalation:
    """E2E Scenario B — escalation banner path (specialist handoff signal)."""

    def test_npi_then_chat_signals_escalation(
        self, api_client, e2e_llm_mocks
    ):
        npi_resp = api_client.get(f"/api/npi/{MOCK_NPI}")
        assert npi_resp.status_code == 200
        practice = npi_resp.json()

        escalation_reply = (
            "Epic integration needs custom setup. I'll connect you with a "
            "PrescriberPoint specialist for the technical details. "
            "Meanwhile, we can still confirm your payer list for prior auth."
        )

        with patch("app.services.ai_service.ChatAnthropic") as mock_llm_cls:
            instance = MagicMock()
            mock_llm_cls.return_value = instance
            instance.invoke.return_value = MagicMock(content=escalation_reply)

            resp = api_client.post(
                "/api/chat",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "We use Epic across three clinic sites and need "
                                "deep EMR integration for prior auth."
                            ),
                        },
                    ],
                    "practice_context": practice,
                    "session_id": "e2e-escalation",
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_escalation"] is True
        assert "prescriberpoint specialist" in data["response"].lower()
        instance.invoke.assert_called_once()
