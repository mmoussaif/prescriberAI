"""Tests for Pydantic models in app.models.schemas."""

import pytest
from pydantic import ValidationError
from app.models.schemas import Provider, PracticeInfo, ChatMessage, ChatRequest, ChatResponse


class TestProvider:
    def test_valid(self):
        p = Provider(name="Dr. Chen", role="Physician", npi="1234567890")
        assert p.name == "Dr. Chen"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            Provider(name="Dr. Chen", role="Physician")


class TestPracticeInfo:
    def test_valid_with_providers(self):
        info = PracticeInfo(
            npi="1234567890",
            practice_name="Springfield Family Medicine",
            address="742 Evergreen Terrace",
            specialty="Family Medicine",
            providers=[Provider(name="Dr. Chen", role="Physician", npi="1234567890")],
        )
        assert len(info.providers) == 1

    def test_empty_providers_list(self):
        info = PracticeInfo(
            npi="1234567890",
            practice_name="Test",
            address="123 Main",
            specialty="Internal Medicine",
            providers=[],
        )
        assert info.providers == []


class TestChatMessage:
    def test_user_message(self):
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"

    def test_assistant_message(self):
        msg = ChatMessage(role="assistant", content="Hi there")
        assert msg.role == "assistant"


class TestChatResponse:
    def test_includes_phase_and_escalation(self):
        resp = ChatResponse(
            response="Welcome!",
            current_phase="patient_demographics",
            needs_escalation=False,
        )
        assert resp.current_phase == "patient_demographics"
        assert resp.needs_escalation is False

    def test_escalation_defaults_to_false(self):
        resp = ChatResponse(response="Hi", current_phase="prior_auth")
        assert resp.needs_escalation is False


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(
            messages=[ChatMessage(role="user", content="Hello")],
            practice_context=PracticeInfo(
                npi="1234567890",
                practice_name="Test",
                address="123 Main",
                specialty="FM",
                providers=[],
            ),
        )
        assert len(req.messages) == 1
