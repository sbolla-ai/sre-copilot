"""Pytest configuration."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is importable when running pytest directly.
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
