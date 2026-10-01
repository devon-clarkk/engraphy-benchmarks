#!/usr/bin/env python3
"""Consolidate the settling runs into the figures the final report quotes.

    python scripts/consolidate.py runs/locomo-settle-a runs/locomo-settle-b ...
    python scripts/consolidate.py --arm=<arm id> <run dir> ...

Reads one arm, the combined engine by default. A run carrying a second arm
has it reported separately, never pooled into the mean.

Each argument is a finished run directory (a strict run, optionally with a
`reference/` pass beside it). Only complete runs are counted: a run whose
manifest carries `quota_stop` or ungraded rows is named and excluded, never
partially averaged.

Prints, for the strict figure and for the reference-convention figure:

- each run's own accuracy, excluding adversarial and per category;
- the mean across runs with the spread (the sample standard deviation, and the
  range when only two runs exist), which is the uncertainty to read a difference
  against;
- the per-category standing against the published Mem0, Mem0-graph and Zep
  figures, aligned to the LoCoMo categories those columns hold.

The comparator columns come from Chhikara et al., arXiv:2504.19413, Table 1,
matched to LoCoMo's categories by the one assignment of the four column names
that reproduces the paper's own overall for all five systems it reports in both
tables (analysis/2026-09-19-locomo-open-domain-findings.md, section 3).
"""

from __future__ import annotations

import json
import math
import pathlib
import statistics
import sys

CATS = ("single-hop", "multi-hop", "temporal-reasoning", "open-domain-knowledge")
# Aligned to the LoCoMo category each paper column holds.
PUBLISHED = {
    "Mem0": {"single-hop": 72.93, "multi-hop": 67.13, "temporal-reasoning": 55.51,
             "open-domain-knowledge": 51.15, "overall": 66.88},
    "Mem0g": {"single-hop": 75.71, "multi-hop": 65.71, "temporal-reasoning": 58.13,
              "open-domain-knowledge": 47.19, "overall": 68.44},
    "Zep": {"single-hop": 76.60, "multi-hop": 61.70, "temporal-reasoning": 49.31,
            "open-domain-knowledge": 41.35, "overall": 65.99},
}


def wilson(k: int, n: int) -> tuple[float, float]:
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


def cell(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.1f}% [{lo:.0f} to {hi:.0f}] ({k}/{n})"


def rows(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def complete(manifest: pathlib.Path) -> tuple[bool, str]:
    if not manifest.exists():
        return False, "no manifest"
    m = json.loads(manifest.read_text(encoding="utf-8"))
    if m.get("quota_stop"):
        return False, f"stopped: {str(m.get('stop_reason', 'usage cap'))[:60]}"
    if m.get("rows_answered_but_ungraded", 0):
        return False, f"{m['rows_answered_but_ungraded']} rows ungraded"
    if not m.get("aggregate"):
        return False, "no aggregate"
    return True, "complete"


# The combined engine, as the harness names an arm in its rows. A run may carry a
# second arm (run A of the settling measurement carries the shipped extraction
# prompt beside it), and pooling two arms into one mean reports a figure no
# configuration produced.
DEFAULT_ARM = "llm_wide-conversational/search_only/always_distinct/k25"


def for_arm(result_rows: list[dict], arm: str) -> list[dict]:
    """One arm's rows, matching the reference pass's suffixed arm name too."""
    return [r for r in result_rows
            if r.get("arm") in (arm, arm + "/reference-conventions")]


def arms_in(result_rows: list[dict]) -> list[str]:
    return sorted({r["arm"].removesuffix("/reference-conventions")
                   for r in result_rows if r.get("arm")})


def buckets(result_rows: list[dict]) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    non_adv = [r for r in result_rows if not r.get("abstain_expected")]
    out["excluding adversarial"] = (sum(bool(r["correct"]) for r in non_adv), len(non_adv))
    if result_rows and len(result_rows) != len(non_adv):
        out["all categories"] = (sum(bool(r["correct"]) for r in result_rows), len(result_rows))
    for c in (*CATS, "adversarial"):
        rs = [r for r in result_rows if r.get("category") == c]
        if rs:
            out[c] = (sum(bool(r["correct"]) for r in rs), len(rs))
    return out


def spread(values: list[float]) -> str:
    if len(values) < 2:
        return "one run, no spread"
    if len(values) == 2:
        return f"range {min(values):.1f} to {max(values):.1f}"
    return f"sd {statistics.stdev(values):.1f}"


def report(title: str, per_run: dict[str, dict[str, tuple[int, int]]]) -> dict[str, float]:
    print(f"\n## {title}  ({len(per_run)} run(s): {', '.join(per_run)})")
    keys: list[str] = []
    for b in per_run.values():
        keys += [k for k in b if k not in keys]
    means: dict[str, float] = {}
    for key in keys:
        cells = [(run, b[key]) for run, b in per_run.items() if key in b]
        accs = [100 * k / n for _, (k, n) in cells]
        means[key] = sum(accs) / len(accs)
        pooled_k = sum(k for _, (k, _) in cells)
        pooled_n = sum(n for _, (_, n) in cells)
        each = "  ".join(f"{run.split('-')[-1]}: {100 * k / n:.1f}%" for run, (k, n) in cells)
        print(f"  {key:24s} mean {means[key]:5.1f}%  ({spread(accs)})  "
              f"pooled {cell(pooled_k, pooled_n)}   [{each}]")
    return means


def standing(means: dict[str, float]) -> None:
    print("\n## per category against the published figures, aligned")
    header = " ".join(f"{k:>7s}" for k in PUBLISHED)
    print(f"  {'category':24s} {'Engraphy':>9s} " + header + "   standing")
    for key, label in [("excluding adversarial", "overall"), *[(c, c) for c in CATS]]:
        if key not in means:
            continue
        ours = means[key]
        pub = {k: v[label if label == "overall" else key] for k, v in PUBLISHED.items()}
        best = max(pub.values())
        worst = min(pub.values())
        verdict = ("ahead of all three" if ours > best else
                   "behind all three" if ours < worst else "inside the published range")
        print(f"  {key:24s} {ours:8.1f}% " + " ".join(f"{pub[k]:7.2f}" for k in PUBLISHED)
              + f"   {verdict}")


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    args = [a for a in sys.argv[1:] if not a.startswith("--arm=")]
    arm = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--arm=")),
               DEFAULT_ARM)
    print(f"arm: {arm}")
    strict: dict[str, dict] = {}
    ref: dict[str, dict] = {}
    for arg in args:
        d = pathlib.Path(arg)
        ok, why = complete(d / "manifest.json")
        print(f"{d.name}: strict {why}")
        if ok:
            all_rows = rows(d / "results.jsonl")
            mine = for_arm(all_rows, arm)
            others = [a for a in arms_in(all_rows) if a != arm]
            if others:
                print(f"{d.name}: reading {len(mine)} rows for this arm, "
                      f"leaving {others} out of the mean")
            if not mine:
                print(f"{d.name}: NO rows for {arm}; it holds {arms_in(all_rows)}")
            else:
                strict[d.name] = buckets(mine)
        ok_r, why_r = complete(d / "reference" / "manifest.json")
        print(f"{d.name}: reference {why_r}")
        if ok_r:
            ref_rows = for_arm(rows(d / "reference" / "results.jsonl"), arm)
            if ref_rows:
                ref[d.name] = buckets(ref_rows)
    if strict:
        strict_title = "strict default (reader may decline, judge requires every gold item)"
        means = report(strict_title, strict)
        standing(means)
    if ref:
        report("under the reference harness conventions", ref)
    if not strict:
        print("\nno complete run yet; nothing is averaged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
