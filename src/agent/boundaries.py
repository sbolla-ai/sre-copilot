"""Boundary enforcement for the agent.

The article's central thesis is that "MCP is not the interesting part. The
boundaries are." This module is where those boundaries live.

Three boundaries are enforced here:
1. Read-only by default — the agent CANNOT call write-path tools
2. Scope limiting — every tool call must specify a service and time window
3. Forced ordering — the deployment timeline is the FIRST tool call, always

NOTE: This module has stubs for you to implement. See `# TODO(you):` markers.
The tests in tests/test_boundaries.py describe the expected behavior.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta


# Tools that NEVER run, regardless of agent reasoning.
# This is the article's "read-only by default" principle, enforced as code.
WRITE_PATH_TOOLS: frozenset[str] = frozenset(
    {
        "create_servicenow_change",
        "acknowledge_pagerduty_incident",
        "restart_service",
        "kubectl_apply",
        "kubectl_delete",
        "rollback_deployment",
    }
)

# Maximum time window any single tool call is allowed to query.
# Bounded data context — the article's second boundary.
MAX_TIME_WINDOW = timedelta(hours=2)

# The MCP tool that MUST be the first call. The article describes this as
# "make the agent use the tools in the order an experienced engineer would."
REQUIRED_FIRST_TOOL: str = "get_deployment_timeline"


@dataclass
class BoundaryViolation(Exception):
    """Raised when the agent attempts a forbidden action."""

    rule: str
    attempted_tool: str
    reason: str

    def __str__(self) -> str:
        return f"Boundary violation [{self.rule}] on tool '{self.attempted_tool}': {self.reason}"


@dataclass
class ToolCallContext:
    """State the boundary system tracks across a single agent run."""

    tool_call_history: list[str] = field(default_factory=list)

    def record(self, tool_name: str) -> None:
        self.tool_call_history.append(tool_name)

    @property
    def is_first_call(self) -> bool:
        return len(self.tool_call_history) == 0


def enforce_read_only(tool_name: str) -> None:
    """Block any write-path tool call, regardless of agent reasoning.

    Article reference: 'Read-only by default. The agent proposes; the human commits.'
    """
    if tool_name in WRITE_PATH_TOOLS:
        raise BoundaryViolation(
            rule="read_only",
            attempted_tool=tool_name,
            reason="Write-path tools are blocked. The agent proposes; the human commits.",
        )


def enforce_scope_limits(
    tool_name: str,
    tool_args: dict,
) -> None:
    """Reject tool calls that don't specify a service AND a tight time window.

    Article reference: 'Bounded data context. Each tool query is scoped to a
    specific service and a tight time window, not the whole observability dataset.'

    TODO(you): Implement this. The tests describe expected behavior.
    A reasonable implementation:
      - Require both `service` and `time_window` keys for query_logs / query_metrics
      - Parse time_window (start, end), reject if end - start > MAX_TIME_WINDOW
      - Reject if `service` is "*" or empty (no whole-lake queries)
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement enforce_scope_limits — see docstring")


def enforce_forced_ordering(
    tool_name: str,
    context: ToolCallContext,
) -> None:
    """Require deployment timeline to be the FIRST tool call.

    Article reference: 'The agent now always checks the deployment timeline as
    its first MCP call, before it touches metrics or traces.'

    Why: Most production incidents in regulated fintech are change-induced.
    Anchoring the agent's reasoning with deploy context up-front dramatically
    reduces the "confident reasoning over wrong evidence" failure mode.
    """
    if context.is_first_call and tool_name != REQUIRED_FIRST_TOOL:
        raise BoundaryViolation(
            rule="forced_ordering",
            attempted_tool=tool_name,
            reason=(
                f"First tool call must be '{REQUIRED_FIRST_TOOL}'. "
                f"Most incidents are change-induced; check deploys first."
            ),
        )


def make_boundary_wrapper(
    tool_fn: Callable,
    tool_name: str,
    context: ToolCallContext,
) -> Callable:
    """Wrap a tool function so all boundary checks fire before the tool runs.

    This is what the agent actually calls. The boundary checks are
    INSIDE the tool wrapper — they cannot be bypassed by clever prompting.
    """

    def wrapped(**tool_args):
        # Order of checks matters: cheapest first, most informative last.
        enforce_read_only(tool_name)
        enforce_forced_ordering(tool_name, context)
        enforce_scope_limits(tool_name, tool_args)

        # All boundaries passed. Record and execute.
        context.record(tool_name)
        return tool_fn(**tool_args)

    wrapped.__name__ = tool_fn.__name__
    wrapped.__doc__ = tool_fn.__doc__
    return wrapped
