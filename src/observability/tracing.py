"""OpenTelemetry instrumentation for the agent.

Article reference: 'I instrumented the entire ReAct loop with OpenTelemetry —
tool-call latency, token counts, retry rates, the JSON of every tool input
and output, model output diffs across runs, and my own feedback signals.'

This module sets up the exporter and provides decorators/spans for the agent
to use.
"""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


_initialized = False


def init_tracing(
    service_name: str = "sre-copilot",
    otlp_endpoint: str | None = None,
) -> None:
    """Initialize OTel tracing once per process.

    By default sends to localhost:4317 (the OTel collector in docker-compose).
    Override with OTEL_EXPORTER_OTLP_ENDPOINT env var or the otlp_endpoint arg.
    """
    global _initialized
    if _initialized:
        return

    endpoint = (
        otlp_endpoint
        or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        or "http://localhost:4317"
    )

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    _initialized = True


def get_tracer() -> trace.Tracer:
    """Get the agent's tracer."""
    return trace.get_tracer("sre-copilot.agent")


@contextmanager
def trace_tool_call(tool_name: str, tool_args: dict[str, Any]):
    """Context manager that wraps a tool call with an OTel span.

    Captures: tool name, tool args (as JSON attribute), latency, success/failure.

    Use this inside the boundary wrapper or directly around tool function calls
    to get full tool-call telemetry.
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)
        # Serialize args carefully — datetime objects need conversion.
        try:
            args_json = json.dumps(tool_args, default=str)
            span.set_attribute("tool.args", args_json)
        except Exception:
            span.set_attribute("tool.args", "<unserializable>")
        try:
            yield span
        except Exception as e:
            span.set_attribute("tool.error", str(e))
            span.set_attribute("tool.success", False)
            raise
        else:
            span.set_attribute("tool.success", True)


def record_recommendation_evidence(
    recommendation_id: str,
    evidence_chain: list[dict[str, Any]],
) -> None:
    """Attach the evidence chain to the current span as a structured attribute.

    Article reference: 'Every recommendation surfaces the underlying tool calls
    — which query, which time window, which deploy diff it looked at.'

    Storing this as a span attribute means you can query it later in your
    OTel backend ('show me all recommendations that cited this Splunk query').
    """
    span = trace.get_current_span()
    span.set_attribute("recommendation.id", recommendation_id)
    span.set_attribute("recommendation.evidence_count", len(evidence_chain))
    span.set_attribute(
        "recommendation.evidence_chain",
        json.dumps(evidence_chain, default=str),
    )
