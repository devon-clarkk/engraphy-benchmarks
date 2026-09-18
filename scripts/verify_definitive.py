#!/usr/bin/env python3
"""Recompute every published figure of the definitive LoCoMo run from the committed files.

    python scripts/verify_definitive.py [results/locomo/locomo-definitive-20260917]

Needs nothing but this repository: no dataset, no engine, no model. It reads the
per-question verdicts and the validity-control outputs and prints

- the strict figure, excluding adversarial and per category;
- the figure under the reference harness conventions, raw;
- its floor: reference answers Engraphy's strict judge also accepts (control A);
- its defensible value: raw, less every credit only the reference rules accept for a
  question whose LoCoMo evidence turns were absent from the retrieved memory;
- the mismatched-answer acceptance of each judge (control B).

To check the verdicts themselves rather than their arithmetic, restore the questions
and gold answers from your own copy of the dataset with scripts/rejoin.py, or rerun
the pipeline with reproduce.py.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

CATS = ("single-hop", "multi-hop", "temporal-reasoning", "open-domain-knowledge")


def rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def wilson(k: int, n: int) -> str:
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * p:.1f}% [{100 * (c - h):.0f} to {100 * (c + h):.0f}] ({k}/{n})"


def main() -> int:
    d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                     else "results/locomo/locomo-definitive-20260917")
    strict = {r["question_id"]: r for r in rows(d / "results.jsonl")}
    ref = {r["question_id"]: r for r in rows(d / "reference" / "results.jsonl")}
    ctl = rows(d / "reference" / "validity_controls.jsonl")
    a = {r["question_id"]: r["strict"] for r in ctl
         if r["control"] == "A_strict_on_reference_answer"}
    b = [r for r in ctl if r["control"] == "B_mismatched"]
    ev = {r["question_id"]: r["evidence_recall"]
          for r in rows(d / "reference" / "evidence_recall.jsonl")}

    non_adv = [r for r in strict.values() if not r.get("abstain_expected")]
    print("strict (reader may decline, judge requires every gold item, best of 3)")
    right = sum(r["correct"] for r in non_adv)
    print(f"  {'excluding adversarial':24s} {wilson(right, len(non_adv))}")
    print(f"  {'all five categories':24s} "
          f"{wilson(sum(r['correct'] for r in strict.values()), len(strict))}")
    for c in (*CATS, "adversarial"):
        cr = [r for r in strict.values() if r["category"] == c]
        print(f"  {c:24s} {wilson(sum(r['correct'] for r in cr), len(cr))}")

    missing = [q for q, r in ref.items() if r["correct"] and q not in a]
    if missing:
        raise SystemExit(f"control A is missing {len(missing)} accepted answers")
    print("\nunder the reference harness conventions, excluding adversarial")
    print(f"  {'category':24s} {'raw':>22s} {'floor':>22s} {'defensible':>22s} removed")
    for c in (*CATS, None):
        qs = [q for q, r in ref.items() if c is None or r["category"] == c]
        raw = [q for q in qs if ref[q]["correct"]]
        floor = [q for q in raw if a[q]]
        removed = [q for q in raw if not a[q] and ev.get(q) == 0]
        n = len(qs)
        print(f"  {c or 'excluding adversarial':24s} {wilson(len(raw), n):>22s} "
              f"{wilson(len(floor), n):>22s} {wilson(len(raw) - len(removed), n):>22s} "
              f"{len(removed)}")
    print(f"\ncontrol B, {len(b)} deliberately mismatched answers: reference judge accepts "
          f"{sum(r['reference'] for r in b)}, strict judge accepts {sum(r['strict'] for r in b)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
