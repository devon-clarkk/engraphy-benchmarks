#!/usr/bin/env python3
"""Render a result directory's PROVENANCE.md from the artifacts it holds.

    python scripts/render_provenance.py results/locomo/<run-id> [--note "..."]

Every figure and every pin in the rendered file is read from `manifest.json`,
`provenance.json` and `config.json` in that directory, never typed by hand, so
the prose cannot disagree with the data it summarises. A field the artifacts do
not carry is printed as "not recorded".
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

NR = "not recorded"


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _pct(b: dict | None) -> str:
    if not b or not b.get("n"):
        return NR
    lo, hi = b["wilson_95"]
    return (f"{100 * b['accuracy']:.1f}% [{100 * lo:.0f} to {100 * hi:.0f}] "
            f"({b['correct']}/{b['n']})")


def _yield(ingest: list[dict]) -> str:
    drafts = sum(r.get("drafts") or 0 for r in ingest)
    nodes = sum(r.get("nodes_written") or 0 for r in ingest)
    if not drafts:
        return NR
    return f"{100 * nodes / drafts:.1f}% ({nodes} of {drafts} extracted memories stored)"


def _served(resolved: dict) -> str:
    """The models the CLI reported per role, without the manifest's prose notes."""
    roles = {k: v for k, v in resolved.items() if not k.endswith("_note")}
    if not roles:
        return NR
    cells = "; ".join(f"{r}: " + ", ".join(f"`{x}`" for x in v) for r, v in sorted(roles.items()))
    if any(isinstance(v, list) and len(v) > 1 for v in roles.values()):
        cells += (" (the CLI reports every model that ran in a call, including one it runs "
                  "for its own internal work, so a role can list two)")
    return cells


def render(d: pathlib.Path, note: str = "") -> str:
    m, p, cfg = _load(d / "manifest.json"), _load(d / "provenance.json"), _load(d / "config.json")
    arms = m.get("aggregate") or {}
    L: list[str] = []
    A = L.append
    A(f"# Provenance: `{m.get('run_id', d.name)}`")
    A("")
    if note:
        A(note)
        A("")

    A("## Result")
    A("")
    for arm, agg in arms.items():
        A(f"Arm `{arm}`, 95% Wilson intervals in brackets.")
        A("")
        A("| | accuracy |")
        A("|---|---|")
        A(f"| **excluding adversarial** | **{_pct(agg.get('overall_excl_adversarial'))}** |")
        A(f"| overall, all five categories | {_pct(agg.get('overall'))} |")
        for cat, b in sorted((agg.get("categories") or {}).items()):
            A(f"| {cat} | {_pct(b)} |")
        A("")
    cal = m.get("judge_calibration") or {}
    inst = cal.get("instability")
    measured = (f"{100 * inst:.1f}% of {cal.get('n', NR)} items"
                if isinstance(inst, (int, float)) else NR)
    A(f"Judge instability, one pass against another on a sample: {measured}.")
    A(f"Write-yield at ingest: {_yield(m.get('ingest') or [])}.")
    A("")

    A("## What ran")
    A("")
    ds = m.get("dataset") or {}
    rm = m.get("role_models") or {}
    def role(r):
        e = rm.get(r) or {}
        return f"`{e.get('model', NR)}` via {e.get('provider', NR)}"
    rows = [
        ("run date", m.get("generated_at", NR)),
        ("engine commit", f"`{m.get('engine_git_sha', NR)}`"),
        ("engine branch", f"`{m.get('git_branch', NR)}`"),
        ("engine tree dirty", str(m.get("git_tree_dirty", NR))),
        ("dataset", f"`{ds.get('path', NR)}` `{ds.get('digest', NR)}`, "
                    f"{ds.get('questions_in_file', NR)} questions in the file"),
        ("conversations", ", ".join(f"`{h}`" for h in m.get("haystacks") or []) or NR),
        ("extractor", role("extractor")),
        ("reader", role("reader")),
        ("judge", role("judge") + f", provider `{m.get('judge_provider', NR)}`"),
        ("reader stance", f"`{(m.get('reader') or {}).get('inference_stance', NR)}`"),
        ("embedding model", f"`{m.get('embedding_model', NR)}` at "
                             f"`{m.get('embedding_revision', NR)}`"),
        ("band thresholds", json.dumps((m.get("band_thresholds") or {}).get("effective", NR))),
        ("prompt hashes", ", ".join(f"`{k}` {v}" for k, v in (m.get("prompt_hashes") or {}).items())
                          or NR),
        ("models that served", _served(m.get("resolved_models") or {})),
    ]
    emb = (cfg.get("embedder") or {})
    if emb:
        rows.append(("embedding profile", f"`{emb.get('profile')}`, onnxruntime "
                     f"{((p.get('runtime') or {}).get('packages') or {}).get('onnxruntime', NR)}"))
    A("| | |")
    A("|---|---|")
    for k, v in rows:
        A(f"| {k} | {v} |")
    A("")

    A("## Where it ran")
    A("")
    if p:
        h, rt, db = p.get("host") or {}, p.get("runtime") or {}, p.get("database") or {}
        A("| | |")
        A("|---|---|")
        A(f"| CPU | {h.get('cpu', NR)}, {h.get('logical_cpus', NR)} logical |")
        A(f"| memory | {h.get('ram_gb', NR)} GB |")
        A(f"| OS | {h.get('os', NR)} |")
        A(f"| Python | {rt.get('python', NR)} |")
        pk = rt.get("packages") or {}
        A("| packages | " + ", ".join(f"{k} {v}" for k, v in pk.items() if v) + " |")
        A(f"| Postgres | {db.get('postgres', NR)}, pgvector {db.get('pgvector', NR)} |")
        A(f"| Docker | {rt.get('docker_server', NR)} |")
        A(f"| Claude Code CLI | {rt.get('claude_cli', NR)} |")
    else:
        A("Host and runtime were not captured for this run.")
    A("")

    A("## Files")
    A("")
    A("- `manifest.json`: the harness manifest, with extracted-memory text removed "
      "from its ingest samples.")
    A("- `results.jsonl`: one row per question, keyed by `question_id`, with the "
      "verdict, the best-of-3 tally and the system's answer. No question text, "
      "gold answers or conversation text; restore them from your own copy with "
      "`scripts/rejoin.py`.")
    A("- `ingest.jsonl`: per-conversation write statistics, including every class "
      "of write refusal and the engine's message for it.")
    if (d / "report.md").exists():
        A("- `report.md`: the harness's rendered report.")
    if (d / "provenance.json").exists():
        A("- `provenance.json`: host, runtime and database versions.")
    if (d / "config.json").exists():
        A("- `config.json`: the configuration this run was produced with.")
    A("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(prog="render_provenance.py")
    ap.add_argument("result_dir", type=pathlib.Path)
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    out = args.result_dir / "PROVENANCE.md"
    out.write_text(render(args.result_dir, args.note), encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
