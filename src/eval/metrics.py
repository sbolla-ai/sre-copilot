"""Eval metrics — comparing agent output to ground-truth root causes."""
from __future__ import annotations

from dataclasses import dataclass

from ..agent.schema import Abstention, AgentOutput, Observation, Recommendation
from ..incidents.types import GroundTruthCause


@dataclass
class IncidentEvalResult:
    """Result of evaluating one incident."""

    incident_id: str
    output_type: str  # "recommendation" | "observation" | "abstention"
    correct: bool
    correct_service_identified: bool
    notes: str = ""


def compare(output: AgentOutput, ground_truth: GroundTruthCause) -> IncidentEvalResult:
    """Compare an agent output to ground truth.

    Scoring rules (deliberate, you can iterate on these):
      - Recommendation that names the right service AND archetype → correct
      - Recommendation that names the wrong service → INCORRECT (confident wrong is worst)
      - Observation that mentions the right service → partial credit (correct=False but
        correct_service_identified=True; tracked separately)
      - Abstention → not correct, not incorrect (recorded as honest unknown)

    The article's central claim is that adding corroboration moves outputs from
    "incorrect Recommendations" toward "correct Recommendations + honest Abstentions"
    rather than just "correct Recommendations." Both are improvements.

    TODO(you): Implement the comparison logic. The Recommendation case is the
    most important — you'll need to extract the service name from the agent's
    free-text root_cause field (regex against the catalog, or have the agent
    emit a structured field).
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement compare — see docstring")
