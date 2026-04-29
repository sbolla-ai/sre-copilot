"""CLI for running the eval suite."""
from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from ..agent.agent import AgentConfig
from .runner import render_summary_table, run_eval_suite


console = Console()


@click.command()
@click.option("--model", default="claude-sonnet-4-5")
@click.option("--output", type=click.Path(path_type=Path))
def main(model: str, output: Path | None) -> None:
    """Run the eval suite against the on-disk eval set."""
    config = AgentConfig(model=model)
    results = run_eval_suite(config=config, output_path=output)
    console.print(render_summary_table(results))


if __name__ == "__main__":
    main()
