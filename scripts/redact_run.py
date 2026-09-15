#!/usr/bin/env python3
"""Write the committable subset of an engine harness run directory.

    python scripts/redact_run.py <engine>/runs/<run-id> results/locomo/<run-id> \
        [--dataset datasets/locomo10.json]

Keeps ids, verdicts, answers, timings and the manifest; drops every piece of
dataset text (see benchkit/redact.py for the exact field list). With --dataset,
report.md is copied only if it quotes no dataset question.
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
    report = args.run_dir / "report.md"
    if report.exists() and args.dataset:
        text = report.read_text(encoding="utf-8")
        found = redact.leaks(text, dataset.question_index(args.dataset))
        if found:
            print(f"report.md withheld: quotes {len(found)} dataset questions, e.g. {found[:3]}")
        else:
            (args.dest / "report.md").write_text(text, encoding="utf-8", newline="\n")
            written["report.md"] = "copied (no dataset questions quoted)"
    for name, what in written.items():
        print(f"{name}: {what}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
