"""Tests for onboarding reply validation helpers."""

from unittest.mock import patch

import app.services.onboarding_validation as ov
from app.services.onboarding_validation import (
    heuristic_reply_quality,
    is_bootstrap_user_message,
    validate_user_reply,
)


def test_bootstrap_detection():
    assert is_bootstrap_user_message(
        "The practice has confirmed their details. Begin the configuration conversation."
    )
    assert not is_bootstrap_user_message("Mostly adults and some geriatric patients.")


def test_heuristic_nonsense_vs_ok():
    assert heuristic_reply_quality("@@@###$$$") == "nonsense"
    assert heuristic_reply_quality("We see adults and geriatric patients, no peds.") == "ok"


def test_validate_user_reply_heuristic_shape():
    with patch.object(ov, "_client", None):
        out = validate_user_reply(
            user_text="Aetna and United; we want PA tracking.",
            last_assistant="Which payers matter most?",
            phase_hint="prior_auth",
        )
    assert out["quality"] in ("ok", "weak", "nonsense")
    assert "sidebar_label" in out
    assert "escalate_suggested" in out
