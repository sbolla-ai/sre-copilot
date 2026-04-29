"""Hardcoded incident fixtures for development iteration.

These are small, hand-built incidents you can use during Phase 1 to test the
agent loop without needing the full generator running. Once Phase 2 generator
is done, you'll mostly use generated incidents instead.

TODO(you): Add at least one fixture here in Phase 1. Suggested structure
is a deploy regression that's small enough to debug by eye.
"""
from __future__ import annotations

from .types import SyntheticIncident


# TODO(you): Populate this dict with fixtures during Phase 1.
# Example:
#   FIXTURES = {
#       "fixture_deploy_001": _build_simple_deploy_regression_fixture(),
#   }
FIXTURES: dict[str, SyntheticIncident] = {}
