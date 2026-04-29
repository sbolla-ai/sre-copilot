"""Tests for the agent output schema.

The Recommendation type enforces the multi-signal rule at construction time.
These tests pin that behavior down — if you ever loosen the schema, these
should fail loudly.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.agent.schema import (
    Abstention,
    Evidence,
    Observation,
    Recommendation,
    SignalType,
)


def make_evidence(signal_type: SignalType, desc: str = "test") -> Evidence:
    return Evidence(
        signal_type=signal_type,
        description=desc,
        tool_call_name="query_metrics",
        tool_call_args={"service": "api-gateway"},
        raw_finding="some finding",
        confidence=0.7,
    )


def test_recommendation_requires_two_signal_types():
    """Multi-signal corroboration is enforced at construction time."""
    with pytest.raises((ValueError, ValidationError)):
        Recommendation(
            root_cause="api-gateway deploy regression",
            confidence=0.8,
            evidence=[make_evidence(SignalType.METRIC_ANOMALY)],
        )


def test_recommendation_rejects_two_evidence_same_signal_type():
    """Two pieces of evidence of the same TYPE is not corroboration."""
    with pytest.raises((ValueError, ValidationError)):
        Recommendation(
            root_cause="api-gateway deploy regression",
            confidence=0.8,
            evidence=[
                make_evidence(SignalType.METRIC_ANOMALY, "p99 spike"),
                make_evidence(SignalType.METRIC_ANOMALY, "error_rate spike"),
            ],
        )


def test_recommendation_accepts_two_independent_signal_types():
    """The happy path: deploy_correlation + metric_anomaly."""
    rec = Recommendation(
        root_cause="api-gateway deploy regression",
        confidence=0.85,
        evidence=[
            make_evidence(SignalType.DEPLOY_CORRELATION),
            make_evidence(SignalType.METRIC_ANOMALY),
        ],
    )
    assert rec.output_type == "recommendation"
    assert len(rec.evidence) == 2


def test_observation_accepts_single_evidence():
    """Observations are the right output for single-signal findings."""
    obs = Observation(
        summary="api-gateway p99 latency is elevated",
        evidence=make_evidence(SignalType.METRIC_ANOMALY),
        suggested_next_step="Check recent deploys to corroborate.",
    )
    assert obs.output_type == "observation"


def test_abstention_can_have_zero_evidence():
    """The honest 'I don't know' path."""
    ab = Abstention(reason="No clear signal in logs or metrics; recommend manual review.")
    assert ab.output_type == "abstention"
    assert ab.partial_evidence == []
