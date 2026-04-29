"""Multi-signal corroboration logic.

The article's central improvement: a root-cause hypothesis must be supported
by at least 2 INDEPENDENT signal types before it can be surfaced as a
recommendation. Single-signal findings become 'observations' instead.

The Recommendation type in schema.py enforces the >=2 signals rule at construction
time. This module is where the AGENT decides what to construct.
"""
from __future__ import annotations

from .schema import Abstention, Evidence, Observation, Recommendation


def synthesize_finding(
    candidate_root_cause: str,
    confidence: float,
    evidence: list[Evidence],
) -> Recommendation | Observation | Abstention:
    """Decide whether the agent's collected evidence justifies a Recommendation,
    an Observation, or an Abstention.

    The article's rule:
      - 2+ independent signal types → Recommendation
      - Exactly 1 signal type → Observation
      - 0 signals or all signals contradict → Abstention

    TODO(you): Implement this. The decision tree is straightforward but the
    tradeoffs are interesting — for example, what do you do when you have
    3 signals all of the same type? (Probably still an Observation, since
    'independent signal TYPES' is what matters for corroboration.)

    The eval harness will measure how this rule affects accuracy on your
    synthetic incident set. If you implement it correctly, you'll see
    accuracy AND honesty improve simultaneously — fewer confident wrongs.
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement synthesize_finding — see docstring")


def count_independent_signals(evidence: list[Evidence]) -> int:
    """How many distinct signal types are in this evidence list?"""
    return len({e.signal_type for e in evidence})
