"""Tests for boundary enforcement.

These tests are a TDD-style spec for src/agent/boundaries.py. They fail until
you implement the stubs in that module. Use them to drive your Phase 1 work.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from src.agent.boundaries import (
    BoundaryViolation,
    REQUIRED_FIRST_TOOL,
    ToolCallContext,
    enforce_forced_ordering,
    enforce_read_only,
    enforce_scope_limits,
)


# ============================================================
# Read-only enforcement
# ============================================================


def test_read_only_blocks_write_path_tools():
    """Write-path tools must always be blocked."""
    with pytest.raises(BoundaryViolation, match="read_only"):
        enforce_read_only("kubectl_apply")


def test_read_only_allows_read_path_tools():
    """Read-path tools should pass through silently."""
    enforce_read_only("query_logs")
    enforce_read_only("query_metrics")
    enforce_read_only("get_deployment_timeline")


def test_read_only_blocks_servicenow_writes():
    with pytest.raises(BoundaryViolation):
        enforce_read_only("create_servicenow_change")


# ============================================================
# Scope limits
# ============================================================


def test_scope_limits_require_service():
    """Tool calls must specify a service."""
    with pytest.raises(BoundaryViolation, match="scope"):
        enforce_scope_limits(
            "query_logs",
            {"time_window_start": datetime.now(), "time_window_end": datetime.now()},
        )


def test_scope_limits_reject_wildcard_service():
    """No querying all services at once."""
    with pytest.raises(BoundaryViolation):
        enforce_scope_limits(
            "query_logs",
            {
                "service": "*",
                "time_window_start": datetime.now(),
                "time_window_end": datetime.now() + timedelta(minutes=10),
            },
        )


def test_scope_limits_reject_overlong_window():
    """Time windows must be <= 2 hours."""
    now = datetime.now()
    with pytest.raises(BoundaryViolation, match="time_window|window"):
        enforce_scope_limits(
            "query_logs",
            {
                "service": "api-gateway",
                "time_window_start": now,
                "time_window_end": now + timedelta(hours=4),
            },
        )


def test_scope_limits_accept_valid_args():
    """Well-formed args should pass through."""
    now = datetime.now()
    enforce_scope_limits(
        "query_logs",
        {
            "service": "api-gateway",
            "time_window_start": now,
            "time_window_end": now + timedelta(minutes=30),
        },
    )


# ============================================================
# Forced ordering
# ============================================================


def test_forced_ordering_requires_deploy_first():
    """First tool call MUST be the deploy timeline."""
    ctx = ToolCallContext()
    with pytest.raises(BoundaryViolation, match="forced_ordering"):
        enforce_forced_ordering("query_logs", ctx)


def test_forced_ordering_allows_deploy_first():
    """Deploy timeline as first call should pass."""
    ctx = ToolCallContext()
    enforce_forced_ordering(REQUIRED_FIRST_TOOL, ctx)


def test_forced_ordering_does_not_apply_after_first_call():
    """Once the deploy timeline has been queried, other tools are fair game."""
    ctx = ToolCallContext()
    ctx.record(REQUIRED_FIRST_TOOL)
    # Should not raise
    enforce_forced_ordering("query_logs", ctx)
    enforce_forced_ordering("query_metrics", ctx)
