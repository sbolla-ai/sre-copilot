"""CLI entry point for running the agent against a single incident."""
from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.panel import Panel

from ..incidents.loader import load_incident
from ..mcp_server.tools import build_tool_set
from .agent import AgentConfig, run_agent


console = Console()


@click.command()
@click.option("--incident-id", required=True, help="ID of the incident to triage.")
@click.option("--model", default="claude-sonnet-4-5", help="Claude model to use.")
@click.option("--output", type=click.Path(), help="Optional path to write run record as JSON.")
def main(incident_id: str, model: str, output: str | None) -> None:
    """Run the agent against a single incident from the eval set."""

    incident = load_incident(incident_id)
    tools = build_tool_set(incident=incident)

    console.print(Panel.fit(f"Running agent against incident: [bold]{incident_id}[/bold]"))

    record = run_agent(
        incident_description=incident.description,
        tools=tools,
        config=AgentConfig(model=model),
    )

    console.print(Panel(str(record.output), title="Agent output"))
    console.print(f"Tool calls: {record.tool_call_count}")
    console.print(f"Tokens: {record.total_input_tokens} in / {record.total_output_tokens} out")

    if output:
        with open(output, "w") as f:
            json.dump(record.model_dump(mode="json"), f, indent=2, default=str)
        console.print(f"Run record written to [cyan]{output}[/cyan]")


if __name__ == "__main__":
    main()
