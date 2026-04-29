"""CLI for incident generation and inspection."""
from __future__ import annotations

import click
from rich.console import Console

from .generator import IncidentGenerator
from .loader import load_incident, save_incident
from .types import IncidentArchetype


console = Console()


@click.group()
def main() -> None:
    """Synthetic incident management."""


@main.command()
@click.option("--archetype", type=click.Choice([a.value for a in IncidentArchetype]))
@click.option("--seed", type=int, default=42)
def generate_one(archetype: str, seed: int) -> None:
    """Generate a single incident and print its summary."""
    gen = IncidentGenerator(seed=seed)
    incident = gen.generate(IncidentArchetype(archetype))
    path = save_incident(incident)
    console.print(f"Generated [bold]{incident.incident_id}[/bold]")
    console.print(f"  Archetype: {incident.ground_truth.archetype}")
    console.print(f"  Primary service: {incident.ground_truth.primary_service}")
    console.print(f"  Saved to: {path}")


@main.command()
@click.argument("incident_id")
def show(incident_id: str) -> None:
    """Print a summary of one incident."""
    incident = load_incident(incident_id)
    console.print(f"[bold]{incident.incident_id}[/bold]")
    console.print(f"  Description: {incident.description}")
    console.print(f"  Detected at: {incident.incident_detected}")
    console.print(f"  {len(incident.log_entries)} log entries")
    console.print(f"  {len(incident.metrics)} metric series")
    console.print(f"  {len(incident.deployments)} deployments in window")
    console.print(f"  Ground truth: {incident.ground_truth.plain_english}")


if __name__ == "__main__":
    main()
