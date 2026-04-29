"""Eval runner — runs the agent against the full eval set, produces a report.

Usage:
  python -m src.eval.runner

Or via the CLI:
  sre-copilot-eval --output reports/eval_2026_04_29.md
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from ..agent.agent import AgentConfig, run_agent
from ..incidents.loader import load_eval_set
from ..mcp_server.tools import build_tool_set
from .metrics import IncidentEvalResult, compare


console = Console()


def run_eval_suite(
    config: AgentConfig | None = None,
    output_path: Path | None = None,
) -> list[IncidentEvalResult]:
    """Run the agent against every incident in the eval set.

    Returns the per-incident results. Optionally writes a markdown report.

    TODO(you): Implement. Suggested approach:
      1. Load the eval set via load_eval_set()
      2. For each incident, build the tool set and call run_agent()
      3. Compare output to ground truth via metrics.compare()
      4. Aggregate into a summary report

    Suggested report contents:
      - Total incidents
      - Per-archetype: correct rate, abstain rate, confident-wrong rate
      - List of all confidently-wrong cases (these are your debugging targets)
      - Tool-call patterns (avg calls per incident, most common first call)
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement run_eval_suite — see docstring")


def render_summary_table(results: list[IncidentEvalResult]) -> Table:
    """Render results as a Rich table for terminal output."""
    table = Table(title="Eval Results")
    table.add_column("Metric")
    table.add_column("Value")

    total = len(results)
    by_type = Counter(r.output_type for r in results)
    correct = sum(1 for r in results if r.correct)
    confident_wrong = sum(
        1 for r in results
        if r.output_type == "recommendation" and not r.correct
    )

    table.add_row("Total incidents", str(total))
    table.add_row("Correct (Recommendation)", str(correct))
    table.add_row("Confident wrong (Recommendation, wrong)", str(confident_wrong))
    table.add_row("Observations", str(by_type.get("observation", 0)))
    table.add_row("Abstentions", str(by_type.get("abstention", 0)))
    if total > 0:
        table.add_row("Accuracy", f"{correct / total:.1%}")
        table.add_row("Confident-wrong rate", f"{confident_wrong / total:.1%}")
    return table
