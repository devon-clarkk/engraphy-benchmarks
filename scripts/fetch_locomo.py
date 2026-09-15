#!/usr/bin/env python3
"""Download LoCoMo from snap-research and verify it against the pinned sha256.

    python scripts/fetch_locomo.py [--dest datasets]

The dataset and its CC BY-NC 4.0 licence are saved side by side. Nothing is
committed: `datasets/` is ignored by git.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from benchkit import ROOT, load_config
from benchkit.dataset import fetch


def main() -> int:
    ap = argparse.ArgumentParser(prog="fetch_locomo.py")
    ap.add_argument("--dest", type=pathlib.Path, default=ROOT / "datasets")
    args = ap.parse_args()
    cfg = load_config()
    path = fetch(cfg, args.dest)
    ds = cfg["dataset"]
    print(f"{path}\nsha256 {ds['sha256']} (verified)\nlicence {ds['license']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
