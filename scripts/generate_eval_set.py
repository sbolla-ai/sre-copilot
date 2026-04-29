#!/usr/bin/env python
"""Generate the on-disk eval set.

Usage:
  python scripts/generate_eval_set.py --n 200 --seed 42
"""
from __future__ import annotations

import click
from rich.console import Console
from rich.progress import track

from src.incidents.generator import IncidentGenerator
from src.incidents.loader import save_incident


console = Console()


@click.command()
@click.option("--n", type=int, default=200, help="Number of incidents to generate.")
@click.option("--seed", type=int, default=42, help="RNG seed for reproducibility.")
def main(n: int, seed: int) -> None:
    """Generate and persist the eval set."""
    gen = IncidentGenerator(seed=seed)
    incidents = gen.generate_eval_set(n=n)

    for incident in track(incidents, description="Saving incidents..."):
        save_incident(incident)

    console.print(f"Generated [bold]{len(incidents)}[/bold] incidents to data/incidents/")


if __name__ == "__main__":
    main()
