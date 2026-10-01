#!/usr/bin/env python3
"""How much of the raw transcript does a store hold verbatim?

    python scripts/turn_verbatim.py --dsn <dsn> --space <space> --extractor llm [...]

Storing turns is a design non-goal: the source-turn layer was measured on
2026-09-25 to cost 8 adversarial declines and was excluded. A wider extraction
prompt stores more, and `retain_source_text` appends the turns a memory cites to
its body, so "more" could in principle approach a transcript by another route.

This measures that directly, with no model in the loop and the same key the
coverage tool uses against evidence turns: a turn counts as held when its first
60 normalised characters appear in some memory of that scope. Evidence coverage
answers whether the store can support the benchmark's questions; this answers
whether the store has become the conversation.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re

import psycopg

PREFIX = 60


def norm(text: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", str(text).lower()).split())


def all_turns(dataset: pathlib.Path) -> dict[str, list[str]]:
    """conversation -> every turn's normalised text, straight from the dataset."""
    out: dict[str, list[str]] = collections.defaultdict(list)
    for sample in json.loads(dataset.read_text(encoding="utf-8")):
        conv = sample.get("conversation") or {}
        for key, sessions in conv.items():
            if not key.startswith("session_") or not isinstance(sessions, list):
                continue
            for turn in sessions:
                text = turn.get("text") or turn.get("clean_text") or ""
                if text:
                    out[sample["sample_id"]].append(norm(text))
    return out


def scope_of(haystack: str, extractor: str) -> str:
    return f"hs-{haystack}-{extractor.replace('_', '-')}"


def bodies(dsn: str, space: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = collections.defaultdict(list)
    with psycopg.connect(dsn) as conn:
        cur = conn.cursor()
        cur.execute("SELECT scope_id, title, body FROM nodes "
                    "WHERE space_id = %s AND status = 'active'", (space,))
        for scope, title, body in cur.fetchall():
            out[scope].append(norm((title or "") + " " + (body or "")))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(prog="turn_verbatim.py")
    ap.add_argument("--dsn", required=True)
    ap.add_argument("--space", action="append", required=True)
    ap.add_argument("--extractor", action="append", required=True)
    ap.add_argument("--haystacks", default="conv-26,conv-30,conv-49")
    ap.add_argument("--dataset", type=pathlib.Path,
                    default=pathlib.Path("datasets/locomo10.json"))
    ap.add_argument("--out", type=pathlib.Path)
    args = ap.parse_args()

    wanted = [h for h in args.haystacks.split(",") if h]
    turns = all_turns(args.dataset)
    report: dict = {"haystacks": wanted, "prefix_chars": PREFIX, "stores": {}}

    for space, extractor in zip(args.space, args.extractor):
        store = bodies(args.dsn, space)
        held = total = 0
        per_conv = {}
        memories = 0
        for haystack in wanted:
            scope_bodies = store.get(scope_of(haystack, extractor), [])
            memories += len(scope_bodies)
            joined = "\n".join(scope_bodies)
            hits = sum(1 for t in turns[haystack] if t[:PREFIX] and t[:PREFIX] in joined)
            per_conv[haystack] = {"turns": len(turns[haystack]), "held_verbatim": hits,
                                  "pct": round(100 * hits / len(turns[haystack]), 1)}
            held += hits
            total += len(turns[haystack])
        report["stores"][f"{space}#{extractor}"] = {
            "memories": memories, "turns": total, "held_verbatim": held,
            "pct": round(100 * held / total, 1) if total else None,
            "per_conversation": per_conv}
        print(f"{extractor:10} {held:5}/{total} turns held verbatim = "
              f"{100 * held / total:5.1f}%   ({memories} memories)")

    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8",
                            newline="\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
