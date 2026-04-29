"""Basic agent integration test.

Run only when ANTHROPIC_API_KEY is set. Skipped otherwise so CI without
secrets doesn't fail.
"""
from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set; skipping live agent test.",
)
def test_agent_runs_against_fixture():
    """End-to-end: load a fixture, run the agent, assert valid output type."""
    from src.agent.agent import AgentConfig, run_agent
    from src.agent.schema import Abstention, Observation, Recommendation
    from src.incidents.fixtures import FIXTURES
    from src.mcp_server.tools import build_tool_set

    if not FIXTURES:
        pytest.skip(
            "No fixtures defined. Add a fixture to src/incidents/fixtures.py to run."
        )

    incident_id, incident = next(iter(FIXTURES.items()))
    tools = build_tool_set(incident=incident)

    record = run_agent(
        incident_description=incident.description,
        tools=tools,
        config=AgentConfig(),
    )

    assert isinstance(record.output, (Recommendation, Observation, Abstention))
    assert record.tool_call_count >= 1
