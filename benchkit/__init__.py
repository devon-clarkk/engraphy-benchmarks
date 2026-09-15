"""Shared helpers for reproduce.py, grade.py and scripts/.

Deliberately small. The benchmark harness itself lives in the engine repository
under `bench/` and is run from a checkout pinned in `config/locomo.json`; nothing
here re-implements extraction, retrieval, reading or judging. What lives here is
everything around the harness that a reproduction needs and the engine repository
has no reason to carry: fetching and verifying the dataset, standing up a
throwaway database, capturing provenance, and stripping dataset-derived text from
results before they are committed.
"""

from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "locomo.json"
WORK = ROOT / "work"


def load_config(path: pathlib.Path = CONFIG_PATH) -> dict:
    """The one config file every entry point reads."""
    return json.loads(path.read_text(encoding="utf-8"))
