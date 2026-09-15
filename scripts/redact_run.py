#!/usr/bin/env python3
"""Write the committable subset of an engine harness run directory.

    python scripts/redact_run.py <engine>/runs/<run-id> results/locomo/<run-id> \
        [--dataset datasets/locomo10.json]

Keeps ids, verdicts, answers, timings and the manifest; drops every piece of
dataset text (see benchkit/redact.py for the exact field list). With --dataset,
every written file is checked for quoted dataset questions, and any hit fails
the run with a non-zero exit.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from benchkit import dataset, redact


def main() -> int:
    ap = argparse.ArgumentParser(prog="redact_run.py")
    ap.add_argument("run_dir", type=pathlib.Path)
    ap.add_argument("dest", type=pathlib.Path)
    ap.add_argument("--dataset", type=pathlib.Path, default=None)
    args = ap.parse_args()

    written = redact.redact_run(args.run_dir, args.dest)
    for name, what in written.items():
        print(f"{name}: {what}")
    if args.dataset:
        hits = redact.check_clean(args.dest, dataset.question_index(args.dataset))
        if hits:
            print(f"dataset questions quoted in {hits}; do not commit {args.dest}")
            return 1
        print("clean: no dataset question is quoted in any written file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
