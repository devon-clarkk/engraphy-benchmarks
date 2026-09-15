#!/usr/bin/env python3
"""Turn an Engraphy harness run into the answers format grade.py reads.

    python scripts/answers_from_run.py work/engraphy/runs/<run-id> \
        --out graded/engraphy-answers.jsonl

Reads the run's `answers.jsonl` (or the committed, redacted `results.jsonl`) and
writes one `{"question_id", "answer"}` row per question. Grading those answers
with grade.py and comparing against the verdicts the harness recorded is how the
grader is checked against the harness.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


def main() -> int:
    ap = argparse.ArgumentParser(prog="answers_from_run.py")
    ap.add_argument("run", type=pathlib.Path, help="a harness run dir, or a results.jsonl")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--limit", type=int, default=0, help="only the first N questions")
    args = ap.parse_args()

    src = args.run
    if src.is_dir():
        names = ("answers.jsonl", "results.jsonl")
        src = next((src / n for n in names if (src / n).exists()), None)
        if src is None:
            raise SystemExit(f"no answers.jsonl or results.jsonl in {args.run}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with src.open(encoding="utf-8") as fin, \
            args.out.open("w", encoding="utf-8", newline="\n") as fout:
        for line in fin:
            if not line.strip():
                continue
            row = json.loads(line)
            fout.write(json.dumps({"question_id": row["question_id"],
                                   "answer": row.get("answer") or ""}, ensure_ascii=False) + "\n")
            n += 1
            if args.limit and n >= args.limit:
                break
    print(f"{n} answers -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
