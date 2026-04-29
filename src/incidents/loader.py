"""Incident loading — from fixtures (hardcoded) or disk (generated eval set)."""
from __future__ import annotations

import json
from pathlib import Path

from .types import SyntheticIncident


# Where the eval set is persisted by scripts/generate_eval_set.py
DEFAULT_INCIDENTS_DIR = Path("data/incidents")


def load_incident(incident_id: str, base_dir: Path | None = None) -> SyntheticIncident:
    """Load a single incident by ID.

    Looks in:
      1. The hardcoded fixtures (for fast iteration during development)
      2. The on-disk eval set (for full eval runs)
    """
    # Check fixtures first
    from . import fixtures
    fixture = fixtures.FIXTURES.get(incident_id)
    if fixture is not None:
        return fixture

    # Fall back to disk
    base_dir = base_dir or DEFAULT_INCIDENTS_DIR
    path = base_dir / f"{incident_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Incident '{incident_id}' not found in fixtures or {base_dir}. "
            f"Generate the eval set with: python scripts/generate_eval_set.py"
        )
    with open(path) as f:
        return SyntheticIncident.model_validate(json.load(f))


def load_eval_set(base_dir: Path | None = None) -> list[SyntheticIncident]:
    """Load the full on-disk eval set."""
    base_dir = base_dir or DEFAULT_INCIDENTS_DIR
    if not base_dir.exists():
        raise FileNotFoundError(
            f"Eval set directory {base_dir} does not exist. "
            f"Generate it with: python scripts/generate_eval_set.py"
        )
    incidents = []
    for path in sorted(base_dir.glob("*.json")):
        with open(path) as f:
            incidents.append(SyntheticIncident.model_validate(json.load(f)))
    return incidents


def save_incident(incident: SyntheticIncident, base_dir: Path | None = None) -> Path:
    """Save an incident to disk."""
    base_dir = base_dir or DEFAULT_INCIDENTS_DIR
    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"{incident.incident_id}.json"
    with open(path, "w") as f:
        json.dump(incident.model_dump(mode="json"), f, indent=2, default=str)
    return path
