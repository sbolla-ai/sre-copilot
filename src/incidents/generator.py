"""Synthetic incident generator.

This is the module the article calls "the hardest part of the project."
The interface is simple but the implementation is where you'll spend most
of your time.

Key design decisions to make as you implement:
  1. How realistic should the synthetic logs/metrics look? Real enough that
     the agent's reasoning patterns transfer to production data, but not
     so real that you spend forever on log syntax fidelity.
  2. How much noise should non-causal services produce? Too little and the
     agent always picks the right service trivially. Too much and even a
     correct agent looks bad.
  3. Misleading correlations are the most important archetype. The article's
     central failure mode (confident reasoning over wrong evidence) only
     appears if your eval set contains incidents where the most-noisy service
     ISN'T the actual cause.

The IncidentGenerator below is a stub. Implement archetype-by-archetype.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from .types import (
    DeploymentEvent,
    GroundTruthCause,
    IncidentArchetype,
    LogEntry,
    MetricPoint,
    MetricSeries,
    SyntheticIncident,
)


# A small synthetic service catalog. Customize as you go.
DEFAULT_SERVICE_NAMES: list[str] = [
    "api-gateway",
    "auth-service",
    "payment-processor",
    "order-service",
    "inventory-service",
    "notification-service",
    "database-proxy",
    "cache-tier",
]


class IncidentGenerator:
    """Generates synthetic incidents with known ground-truth causes."""

    def __init__(
        self,
        services: list[str] | None = None,
        seed: int = 42,
    ) -> None:
        self.services = services or DEFAULT_SERVICE_NAMES
        self.rng = random.Random(seed)

    def generate(self, archetype: IncidentArchetype) -> SyntheticIncident:
        """Generate a single incident of the given archetype.

        Dispatches to the per-archetype builder.
        """
        builders = {
            IncidentArchetype.DEPLOY_REGRESSION: self._build_deploy_regression,
            IncidentArchetype.DOWNSTREAM_DEPENDENCY_DEGRADATION: (
                self._build_downstream_dependency
            ),
            IncidentArchetype.NOISY_NEIGHBOR: self._build_noisy_neighbor,
            IncidentArchetype.MISLEADING_CORRELATION: self._build_misleading_correlation,
        }
        builder = builders.get(archetype)
        if builder is None:
            raise NotImplementedError(f"Archetype {archetype} not implemented yet.")
        return builder()

    def generate_eval_set(
        self,
        n: int = 200,
        archetype_mix: dict[IncidentArchetype, float] | None = None,
    ) -> list[SyntheticIncident]:
        """Generate a full eval set with a given archetype distribution.

        Default mix is uniform across implemented archetypes.

        TODO(you): Once you have multiple archetypes, the right mix becomes
        an interesting design choice. The article's "misleading correlation"
        case is the most diagnostic — under-weighting it means your eval set
        won't surface the failure mode the article is built around. Consider
        oversampling it.
        """
        # TODO(you): replace this stub
        raise NotImplementedError("Implement generate_eval_set — see docstring")

    # ============================================================
    # Per-archetype builders. Implement these one at a time.
    # ============================================================

    def _build_deploy_regression(self) -> SyntheticIncident:
        """A deploy lands, metrics degrade shortly after.

        The canonical 'easy' case. If your agent can't catch this, fix that first.

        TODO(you): Implement. Suggested shape:
          - Pick a primary service from the catalog
          - Generate a deploy event ~30 min before incident start
          - Generate metrics where this service's error_rate or latency spikes
          - Generate logs from this service showing the new error pattern
          - Generate "normal" data for all other services
          - Ground truth: archetype=DEPLOY_REGRESSION, signal_types include
            deploy_correlation + metric_anomaly + log_pattern
        """
        raise NotImplementedError("Implement _build_deploy_regression")

    def _build_downstream_dependency(self) -> SyntheticIncident:
        """A downstream service degrades, callers see knock-on effects.

        Trickier — multiple services look bad, but only one is actually
        causal. The agent should follow the dependency chain.

        TODO(you): Implement.
        """
        raise NotImplementedError("Implement _build_downstream_dependency")

    def _build_noisy_neighbor(self) -> SyntheticIncident:
        """Resource contention from a co-located workload.

        TODO(you): Implement. The "smoking gun" here is correlated CPU/memory
        spikes on the noisy neighbor without any deploy or downstream event.
        """
        raise NotImplementedError("Implement _build_noisy_neighbor")

    def _build_misleading_correlation(self) -> SyntheticIncident:
        """The most important archetype.

        A service is historically noisy at this time of day. A real incident
        is happening elsewhere (a deploy, say), but the noisy service is the
        most "obvious" pattern in the data.

        This is the archetype that surfaces the article's central failure
        mode: confident reasoning over wrong evidence. If your agent passes
        the deploy regression and downstream cases but FAILS this one, your
        eval set has done its job.

        TODO(you): Implement carefully. The structure:
          - Real cause: a deploy regression on service A
          - Misleading signal: service B is showing its usual time-of-day noise
          - Without forced ordering / corroboration, the agent will pick B
          - With forced ordering / corroboration, the agent should pick A
        """
        raise NotImplementedError("Implement _build_misleading_correlation")

    # ============================================================
    # Helpers — implement as you need them
    # ============================================================

    def _generate_baseline_metric_series(
        self,
        service: str,
        name: str,
        start: datetime,
        end: datetime,
        baseline_value: float,
        noise_pct: float = 0.1,
    ) -> MetricSeries:
        """Generate a normal metric series with light noise.

        TODO(you): Implement. Suggested approach:
          - One MetricPoint per minute between start and end
          - Each value = baseline * (1 + noise_pct * gaussian())
          - baseline_p50 = baseline, baseline_p99 = baseline * 1.5 (or similar)
        """
        raise NotImplementedError("Implement _generate_baseline_metric_series")

    def _inject_anomaly(
        self,
        series: MetricSeries,
        start: datetime,
        magnitude: float,
        duration: timedelta,
    ) -> MetricSeries:
        """Take a baseline series and overlay an anomaly starting at 'start'.

        TODO(you): Implement. The magnitude is a multiplier on the baseline.
        For a 'spike,' magnitude=5.0 means values become 5x normal during the
        anomaly window.
        """
        raise NotImplementedError("Implement _inject_anomaly")
