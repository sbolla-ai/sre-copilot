"""Output schema for the agent.

The article describes an important distinction: a "recommendation" requires
multi-signal corroboration, while an "observation" is a single-signal finding
that hasn't been corroborated. This module defines those types.

These are deliberately strict Pydantic models so the agent can't hand-wave
its way around the corroboration rule.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """The kinds of independent evidence the agent can find."""

    DEPLOY_CORRELATION = "deploy_correlation"
    METRIC_ANOMALY = "metric_anomaly"
    LOG_PATTERN = "log_pattern"
    TRACE_ANOMALY = "trace_anomaly"
    DEPENDENCY_DEGRADATION = "dependency_degradation"


class Evidence(BaseModel):
    """A single piece of evidence the agent gathered.

    The article's "visible evidence chain" UX is built on this type — every
    finding has to point at the tool call that produced it.
    """

    signal_type: SignalType
    description: str
    tool_call_name: str = Field(
        description="Which MCP tool produced this evidence — for the evidence chain UI."
    )
    tool_call_args: dict[str, Any]
    raw_finding: str = Field(
        description="The actual data the tool returned that supports this evidence."
    )
    confidence: float = Field(ge=0.0, le=1.0)


class Observation(BaseModel):
    """A single-signal finding. NOT a recommendation.

    Per the article's corroboration rule, the agent surfaces single-signal
    findings as 'observations' rather than recommendations.
    """

    output_type: str = Field(default="observation", frozen=True)
    summary: str
    evidence: Evidence
    suggested_next_step: str | None = Field(
        default=None,
        description="What signal would corroborate this and turn it into a recommendation.",
    )


class Recommendation(BaseModel):
    """A multi-signal corroborated root-cause hypothesis.

    Per the article's corroboration rule, this requires AT LEAST 2 independent
    signals. Construction enforces this — see __init__.
    """

    output_type: str = Field(default="recommendation", frozen=True)
    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(min_length=2)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        signal_types = {e.signal_type for e in self.evidence}
        if len(signal_types) < 2:
            raise ValueError(
                f"Recommendation requires >=2 INDEPENDENT signal types, "
                f"got {len(signal_types)}: {signal_types}. "
                f"Surface this as an Observation instead."
            )


class Abstention(BaseModel):
    """Explicit 'I don't know' output.

    The article's eval-harness reward for declining when uncertain produces this
    output. This is the third valid response type alongside Observation and
    Recommendation — fabricated chains of reasoning are NOT a valid response.
    """

    output_type: str = Field(default="abstention", frozen=True)
    reason: str = Field(description="Why the agent declined to produce a finding.")
    partial_evidence: list[Evidence] = Field(
        default_factory=list,
        description="What the agent did find before deciding it wasn't enough.",
    )


# Union type for all valid agent outputs.
AgentOutput = Recommendation | Observation | Abstention


class AgentRunRecord(BaseModel):
    """A complete record of one agent run, for the eval harness and observability."""

    incident_id: str
    started_at: datetime
    finished_at: datetime
    output: AgentOutput
    tool_call_count: int
    total_input_tokens: int
    total_output_tokens: int
    tool_call_log: list[dict[str, Any]] = Field(
        description="Ordered log of every tool call. Used for evidence chains and OTel spans."
    )
