#!/usr/bin/env python3
"""Restore question and gold answer to committed results, from your own copy of LoCoMo.

    python scripts/fetch_locomo.py
    python scripts/rejoin.py results/locomo/<run-id>/results.jsonl --out audit/<run-id>.jsonl

Committed results carry question ids, never dataset text. This joins them with the
dataset you downloaded, so every verdict can be read beside the question it
answered and the gold it was graded against. The output lands under `audit/`,
which git ignores, so the joined file is never committed back.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from benchkit import ROOT, load_config
from benchkit.dataset import question_index, verify


def main() -> int:
    ap = argparse.ArgumentParser(prog="rejoin.py")
    ap.add_argument("results", type=pathlib.Path)
    ap.add_argument("--dataset", type=pathlib.Path, default=ROOT / "datasets" / "locomo10.json")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    verify(args.dataset, load_config()["dataset"]["sha256"])
    index = question_index(args.dataset)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    joined = missing = 0
    with args.results.open(encoding="utf-8") as fin, \
            args.out.open("w", encoding="utf-8", newline="\n") as fout:
        for line in fin:
            if not line.strip():
                continue
            row = json.loads(line)
            q = index.get(row.get("question_id"))
            if q is None:
                missing += 1
            else:
                row = {**row, "question_text": q["question"], "gold_answer": q["gold_answer"]}
                joined += 1
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{joined} rows joined, {missing} without a matching question -> {args.out}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
