"""Type definitions for synthetic incidents.

A synthetic incident has three things:
  1. The synthetic data (logs, metrics, deploys) the agent will query
  2. A natural-language description for the agent's prompt
  3. The ground-truth root cause, used by the eval harness

The third part is what makes the eval harness work. Real-world incidents
have ambiguous root causes; synthetic ones have known answers.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IncidentArchetype(str, Enum):
    """The kinds of incidents the generator can produce.

    Per PROJECT_STATUS Phase 2, you should implement at least these four.
    Add more as you find interesting failure modes in your eval runs.
    """

    DEPLOY_REGRESSION = "deploy_regression"
    DOWNSTREAM_DEPENDENCY_DEGRADATION = "downstream_dependency_degradation"
    NOISY_NEIGHBOR = "noisy_neighbor"
    MISLEADING_CORRELATION = "misleading_correlation"
    # Future ideas: cache stampede, certificate expiry, dns flap, OOM, etc.


class GroundTruthCause(BaseModel):
    """The actual cause of the incident, known at generation time.

    The eval harness compares the agent's Recommendation against this.
    """

    archetype: IncidentArchetype
    primary_service: str = Field(
        description="The service that actually caused the incident."
    )
    causal_signal_types: list[str] = Field(
        description=(
            "Which signal types should the agent be able to corroborate? "
            "E.g., for a deploy regression: ['deploy_correlation', 'metric_anomaly']."
        )
    )
    plain_english: str = Field(
        description="Short plain-English description for eval reports."
    )


class LogEntry(BaseModel):
    timestamp: datetime
    service: str
    level: str
    message: str


class MetricPoint(BaseModel):
    timestamp: datetime
    value: float


class MetricSeries(BaseModel):
    service: str
    name: str
    points: list[MetricPoint]
    # Baseline for anomaly detection, generated at incident creation time.
    baseline_p50: float
    baseline_p99: float


class DeploymentEvent(BaseModel):
    timestamp: datetime
    service: str
    version: str
    change_summary: str


class SyntheticIncident(BaseModel):
    """A complete synthetic incident the agent can be tested against."""

    incident_id: str
    description: str = Field(
        description="The page text the on-call engineer would see — agent's input."
    )
    incident_start: datetime = Field(
        description="When the incident begins (reflected in metric/log anomalies)."
    )
    incident_detected: datetime = Field(
        description="When the page would have fired."
    )

    # Synthetic data the agent queries via MCP tools.
    log_entries: list[LogEntry]
    metrics: list[MetricSeries]
    deployments: list[DeploymentEvent]

    # The answer, used only by the eval harness.
    ground_truth: GroundTruthCause

    # Provenance — useful for reproducing/debugging incidents.
    generator_seed: int
    generator_metadata: dict[str, Any] = Field(default_factory=dict)
