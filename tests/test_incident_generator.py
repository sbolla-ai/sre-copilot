"""Tests for the synthetic incident generator.

These tests fail until you implement the generator. They specify the contract
the generator must meet.
"""
from __future__ import annotations

import pytest

from src.incidents.generator import IncidentGenerator
from src.incidents.types import IncidentArchetype


def test_deploy_regression_has_deploy_in_window():
    """A deploy regression incident must include a deploy event."""
    gen = IncidentGenerator(seed=1)
    incident = gen.generate(IncidentArchetype.DEPLOY_REGRESSION)
    deploys_for_primary = [
        d for d in incident.deployments
        if d.service == incident.ground_truth.primary_service
    ]
    assert len(deploys_for_primary) >= 1, (
        "Deploy regression must have at least one deploy on the primary service"
    )


def test_deploy_regression_deploy_precedes_incident():
    """Deploy must come BEFORE incident start (otherwise it's not the cause)."""
    gen = IncidentGenerator(seed=1)
    incident = gen.generate(IncidentArchetype.DEPLOY_REGRESSION)
    primary_deploys = [
        d for d in incident.deployments
        if d.service == incident.ground_truth.primary_service
    ]
    assert all(d.timestamp < incident.incident_start for d in primary_deploys)


def test_misleading_correlation_primary_service_is_NOT_noisy_one():
    """The whole point of this archetype: the obvious-looking service is wrong."""
    gen = IncidentGenerator(seed=2)
    incident = gen.generate(IncidentArchetype.MISLEADING_CORRELATION)
    # The primary (causal) service should not be the most-noisy one in metrics.
    # This test will need refinement once you implement the archetype, but the
    # spirit is: a naive "pick the loudest service" agent should get this wrong.
    # TODO(you): refine the assertion based on how you implement the archetype.
    assert incident.ground_truth.archetype == IncidentArchetype.MISLEADING_CORRELATION


def test_eval_set_size():
    """generate_eval_set produces the requested number of incidents."""
    gen = IncidentGenerator(seed=3)
    incidents = gen.generate_eval_set(n=20)
    assert len(incidents) == 20


def test_eval_set_archetype_diversity():
    """An eval set should include all four archetypes by default."""
    gen = IncidentGenerator(seed=4)
    incidents = gen.generate_eval_set(n=40)
    archetypes_seen = {i.ground_truth.archetype for i in incidents}
    assert len(archetypes_seen) >= 4, (
        f"Expected all 4 archetypes, got: {archetypes_seen}"
    )


def test_incidents_are_deterministic_under_seed():
    """Same seed → same incidents. Important for reproducible eval runs."""
    gen1 = IncidentGenerator(seed=42)
    gen2 = IncidentGenerator(seed=42)
    inc1 = gen1.generate(IncidentArchetype.DEPLOY_REGRESSION)
    inc2 = gen2.generate(IncidentArchetype.DEPLOY_REGRESSION)
    assert inc1.ground_truth.primary_service == inc2.ground_truth.primary_service
