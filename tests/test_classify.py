"""Tests for the classify_phase logic — keyword fallback and parsing."""

from app.services.ai_service import (
    _classify_with_keywords,
    check_complete,
    ESCALATION_SIGNALS,
    CONFIG_AREAS,
    _THINK_RE,
)


class TestKeywordClassifier:
    def test_empty_conversation_returns_first_area(self):
        messages = [{"role": "user", "content": "Begin configuration."}]
        assert _classify_with_keywords(messages) == "patient_demographics"

    def test_demographics_covered_advances_to_prescribing(self):
        messages = [
            {"role": "user", "content": "Begin."},
            {"role": "assistant", "content": "What age group do you serve?"},
            {"role": "user", "content": "Adults only, some geriatric patients."},
        ]
        assert _classify_with_keywords(messages) == "prescribing_focus"

    def test_gibberish_does_not_advance_when_ai_used_no_keywords(self):
        messages = [
            {"role": "user", "content": "Begin."},
            {"role": "assistant", "content": "Tell me about your patients."},
            {"role": "user", "content": "asdfghjkl"},
        ]
        assert _classify_with_keywords(messages) == "patient_demographics"

    def test_keyword_fallback_known_limitation(self):
        """Keyword fallback advances when AI's question contains area keywords.
        This is a known limitation — the LLM classifier (Qwen) handles this correctly."""
        messages = [
            {"role": "user", "content": "Begin."},
            {"role": "assistant", "content": "What age group do you serve — pediatric, adult, geriatric?"},
            {"role": "user", "content": "asdfghjkl"},
        ]
        result = _classify_with_keywords(messages)
        assert result != "patient_demographics", "Keywords in AI question trigger false advance"


class TestThinkTagParsing:
    def test_strips_think_tags(self):
        raw = "<think>\nLet me analyze...\n</think>\npatient_demographics"
        cleaned = _THINK_RE.sub("", raw).strip().lower()
        assert cleaned == "patient_demographics"

    def test_handles_no_think_tags(self):
        raw = "prescribing_focus"
        cleaned = _THINK_RE.sub("", raw).strip().lower()
        assert cleaned == "prescribing_focus"

    def test_handles_multiline_think(self):
        raw = "<think>\nLine 1\nLine 2\nLine 3\n</think>\nsummary"
        cleaned = _THINK_RE.sub("", raw).strip().lower()
        assert cleaned == "summary"


class TestCheckComplete:
    def test_detects_configuration_complete(self):
        state = {
            "messages": [],
            "practice_context": {},
            "current_phase": "summary",
            "is_complete": False,
            "needs_escalation": False,
            "response": "CONFIGURATION COMPLETE\n\nHere is your setup...",
        }
        result = check_complete(state)
        assert result["is_complete"] is True

    def test_case_insensitive_detection(self):
        state = {
            "messages": [],
            "practice_context": {},
            "current_phase": "summary",
            "is_complete": False,
            "needs_escalation": False,
            "response": "Configuration Complete - here's your summary.",
        }
        result = check_complete(state)
        assert result["is_complete"] is True

    def test_no_completion_in_normal_response(self):
        state = {
            "messages": [],
            "practice_context": {},
            "current_phase": "patient_demographics",
            "is_complete": False,
            "needs_escalation": False,
            "response": "What age groups do you serve?",
        }
        result = check_complete(state)
        assert result["is_complete"] is False

    def test_detects_escalation_signal(self):
        state = {
            "messages": [],
            "practice_context": {},
            "current_phase": "prior_auth",
            "is_complete": False,
            "needs_escalation": False,
            "response": "I'll connect you with a PrescriberPoint specialist for the multi-site setup.",
        }
        result = check_complete(state)
        assert result["needs_escalation"] is True
        assert result["is_complete"] is False

    def test_no_escalation_in_normal_response(self):
        state = {
            "messages": [],
            "practice_context": {},
            "current_phase": "prior_auth",
            "is_complete": False,
            "needs_escalation": False,
            "response": "Which payers do you work with most?",
        }
        result = check_complete(state)
        assert result["needs_escalation"] is False

    def test_all_escalation_signals_are_lowercase(self):
        for signal in ESCALATION_SIGNALS:
            assert signal == signal.lower(), f"Signal must be lowercase: {signal}"

    def test_config_areas_order(self):
        expected = [
            "patient_demographics",
            "prescribing_focus",
            "prior_auth",
            "sample_management",
            "coverage_affordability",
            "provider_roles",
        ]
        assert CONFIG_AREAS == expected
