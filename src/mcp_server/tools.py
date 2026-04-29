"""MCP tools exposed to the agent.

These are the tools the agent can call via the Model Context Protocol.
The tool surface is deliberately Splunk-shaped (query_logs, query_metrics)
because that mirrors the production observability stack the article describes,
and makes the project's lessons portable.

For the side project, these tools query a synthetic dataset (loaded from the
incident under test) rather than a live observability stack.

NOTE: This module has stubs for you to implement. See `# TODO(you):` markers.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..incidents.types import SyntheticIncident


# ============================================================
# Tool argument schemas — used by both LangChain and MCP
# ============================================================


class QueryLogsArgs(BaseModel):
    """Arguments for querying logs."""

    service: str = Field(description="The service name to query. Cannot be '*' or empty.")
    time_window_start: datetime = Field(description="Start of query window (ISO 8601).")
    time_window_end: datetime = Field(description="End of query window (ISO 8601).")
    log_level: str | None = Field(
        default=None,
        description="Optional filter: 'ERROR', 'WARN', 'INFO'. Omit for all levels.",
    )
    pattern: str | None = Field(
        default=None,
        description="Optional substring to filter log messages. Case-sensitive.",
    )


class QueryMetricsArgs(BaseModel):
    """Arguments for querying metrics."""

    service: str = Field(description="The service name to query. Cannot be '*' or empty.")
    metric_name: str = Field(
        description="Metric to query (e.g., 'request_latency_p99', 'error_rate', 'cpu_pct')."
    )
    time_window_start: datetime
    time_window_end: datetime


class GetDeploymentTimelineArgs(BaseModel):
    """Arguments for the deployment timeline tool.

    Note: This tool is REQUIRED to be the first call. The boundary system
    enforces it. The agent prompt explains it. Do not change this without
    updating both.
    """

    time_window_start: datetime = Field(
        description="Start of deploy window — typically 2 hours before incident start."
    )
    time_window_end: datetime = Field(
        description="End of deploy window — typically the incident detection time."
    )
    service: str | None = Field(
        default=None,
        description="Optional service filter. Omit to see all deploys in window.",
    )


# ============================================================
# Tool implementations
# ============================================================


def query_logs(
    incident: "SyntheticIncident",
    service: str,
    time_window_start: datetime,
    time_window_end: datetime,
    log_level: str | None = None,
    pattern: str | None = None,
) -> str:
    """Query logs from the synthetic dataset for the incident under test.

    Returns a string formatted to look like Splunk output, so the agent's
    parsing of real-world Splunk responses also works here.

    TODO(you): Implement this. Suggested approach:
      1. Filter incident.log_entries by service, time window, level, pattern
      2. Format results as `<timestamp> <level> <service> <message>` lines
      3. If 0 results, return a clear "No logs found" message (not empty string)
      4. Cap output at ~50 lines — truncate with a summary line if more

    Why a string and not a list of objects: ReAct agents handle text better
    than structured data, and this matches what real Splunk would return via
    the search API.
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement query_logs — see docstring")


def query_metrics(
    incident: "SyntheticIncident",
    service: str,
    metric_name: str,
    time_window_start: datetime,
    time_window_end: datetime,
) -> str:
    """Query a metric time series from the synthetic dataset.

    TODO(you): Implement this. Suggested approach:
      1. Filter incident.metrics by service and name
      2. Filter the time series points to the requested window
      3. Return a summary: min, max, mean, p50, p95, p99, plus first/last values
      4. If anomaly is detected (e.g., p99 > 3x baseline), say so explicitly —
         this is what gives the agent something concrete to corroborate against
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement query_metrics — see docstring")


def get_deployment_timeline(
    incident: "SyntheticIncident",
    time_window_start: datetime,
    time_window_end: datetime,
    service: str | None = None,
) -> str:
    """Return deploys in the given window. ALWAYS the first tool call.

    TODO(you): Implement this. Suggested approach:
      1. Filter incident.deployments by time window and optional service
      2. For each deploy, return: timestamp, service, version, brief change summary
      3. If 0 deploys in window, say so clearly — "No deploys in last 2h" is
         itself useful evidence (rules out change-induced incidents)

    Why this is forced first: the article explains it. Most production
    incidents in regulated fintech are change-induced. Anchoring the agent's
    reasoning with deploy context up front dramatically reduces the
    "confident reasoning over wrong evidence" failure mode.
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement get_deployment_timeline — see docstring")


# ============================================================
# Tool registry — what the agent gets handed
# ============================================================


def build_tool_set(incident: "SyntheticIncident") -> list[StructuredTool]:
    """Build the LangChain tool set, bound to a specific incident.

    The agent sees these as MCP tools; the boundary wrapper in agent.py
    intercepts every call before it reaches the function below.
    """
    return [
        StructuredTool.from_function(
            func=lambda **kw: get_deployment_timeline(incident=incident, **kw),
            name="get_deployment_timeline",
            description=(
                "REQUIRED FIRST TOOL. Returns deploys in a time window. "
                "Most incidents are change-induced; check this first. "
                "Args: time_window_start, time_window_end, optional service."
            ),
            args_schema=GetDeploymentTimelineArgs,
        ),
        StructuredTool.from_function(
            func=lambda **kw: query_logs(incident=incident, **kw),
            name="query_logs",
            description=(
                "Query logs for a specific service in a tight time window. "
                "Cannot query all services. Cannot query windows >2h. "
                "Args: service, time_window_start, time_window_end, optional log_level, optional pattern."
            ),
            args_schema=QueryLogsArgs,
        ),
        StructuredTool.from_function(
            func=lambda **kw: query_metrics(incident=incident, **kw),
            name="query_metrics",
            description=(
                "Query a metric time series for a specific service. "
                "Returns summary stats and an anomaly flag if detected. "
                "Args: service, metric_name, time_window_start, time_window_end."
            ),
            args_schema=QueryMetricsArgs,
        ),
    ]
