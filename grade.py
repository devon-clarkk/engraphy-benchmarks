#!/usr/bin/env python3
"""Score any memory system's LoCoMo answers with the judge that scored Engraphy.

    python grade.py answers.jsonl --system my-memory-system

`answers.jsonl` holds one row per question:

    {"question_id": "conv-26:q0", "answer": "..."}

Question ids follow the engine loader's scheme, `{sample_id}:q{j}` with `j` the
0-based index into that conversation's `qa` list. Produce the answers however
your system produces them: ingest the conversations, retrieve, read. This script
does the part that has to be identical across systems for two numbers to mean
the same thing:

* the same judge model, prompt and best-of-3 majority the Engraphy figure used,
  imported from the pinned engine checkout rather than copied;
* the same rule for the adversarial category, graded on whether the system
  declined rather than by the judge;
* the same per-category aggregation with 95% Wilson intervals, and both
  denominators, overall and excluding adversarial.

Every question of every conversation your file touches is expected. A question
with no row counts as wrong, never as a correct abstention, so coverage cannot
flatter a score. Grading is checkpointed per question; run the same command
again to resume.

The reader is yours, and the reader matters. Two systems graded here differ in
their memory and in whatever model reads it; METHODOLOGY.md says what that does
and does not let you conclude.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from benchkit import ROOT, WORK, dataset, engine, load_config

HERE = pathlib.Path(__file__).resolve().parent


def _outer(argv: list[str]) -> int:
    """Put the pinned engine in place, then re-run this script inside its venv."""
    cfg = load_config()
    eng = engine.ensure_checkout(cfg, WORK)
    py = engine.ensure_venv(WORK, eng)
    data = dataset.fetch(cfg, ROOT / "datasets")
    env = dict(os.environ, BENCHKIT_INNER="1", BENCHKIT_DATASET=str(data))
    for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        env.pop(var, None)
    return subprocess.run([str(py), str(HERE / "grade.py"), *argv], env=env).returncode


def _inner(args: argparse.Namespace) -> int:
    from bench.adapters.locomo import LoCoMoLoader
    from bench.core.judge import JUDGE_PASSES, Judge
    from bench.core.llm import ROLE_MODELS, prompt_hash
    from bench.core.providers import ClaudeCLIClient, GeminiClient, QuotaExhausted
    from bench.core.report import aggregate
    from bench.core.score import LLMJudgeScorer

    cfg = load_config()
    data = pathlib.Path(os.environ["BENCHKIT_DATASET"])
    corpus = LoCoMoLoader().load(data)
    by_id = {q.question_id: q for q in corpus.questions}

    answers: dict[str, str] = {}
    for n, line in enumerate(args.answers.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        qid = row.get("question_id")
        if qid not in by_id:
            raise SystemExit(f"{args.answers}:{n}: unknown question_id {qid!r}")
        answers[qid] = str(row.get("answer") or "")

    covered = sorted({by_id[q].haystack_id for q in answers})
    expected = [q for q in corpus.questions if q.haystack_id in covered]

    judge_model = (cfg["models"]["judge"] if args.judge == "claude"
                   else ROLE_MODELS["judge"]["model"])

    def make_judge() -> Judge:
        client = (ClaudeCLIClient(model=judge_model) if args.judge == "claude"
                  else GeminiClient(model=judge_model))
        return Judge(client)

    out = args.out or (ROOT / "graded" / args.system)
    out.mkdir(parents=True, exist_ok=True)
    graded_path = out / "graded.jsonl"
    done = {}
    if graded_path.exists():
        for line in graded_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["question_id"]] = r

    scorer = LLMJudgeScorer()

    def base(q) -> dict:
        return {"arm": args.system, "question_id": q.question_id, "haystack_id": q.haystack_id,
                "category": q.category, "abstain_expected": q.abstain_expected}

    todo = [q for q in expected if q.question_id not in done]
    print(f"{len(expected)} questions across {', '.join(covered)}; "
          f"{len(answers)} answered, {len(done)} already graded, {len(todo)} to grade", flush=True)

    def grade_one(q):
        if q.question_id not in answers:
            return {**base(q), "answer": None, "correct": False, "graded_by": "missing",
                    "reason": "no answer supplied", "judge_model": "", "judge_seconds": 0.0,
                    "judge_error": ""}
        v = scorer.grade(q, answers[q.question_id], make_judge())
        return {**base(q), "answer": answers[q.question_id], **v.as_dict()}

    stopped = None
    with graded_path.open("a", encoding="utf-8", newline="\n") as fh, \
            cf.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futures = {pool.submit(grade_one, q): q for q in todo}
        for fut in cf.as_completed(futures):
            try:
                row = fut.result()
            except QuotaExhausted as exc:
                stopped = str(exc)
                continue
            if row["graded_by"] == "judge_error":
                continue  # never checkpointed; a resume grades it again
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            done[row["question_id"]] = row

    if stopped or len(done) < len(expected):
        print(f"\nstopped with {len(done)}/{len(expected)} graded"
              + (f" ({stopped})" if stopped else "") + ". Run the same command to resume.")
        return 1

    rows = [done[q.question_id] for q in expected]
    summary = {
        "system": args.system,
        "answers_sha256": hashlib.sha256(args.answers.read_bytes()).hexdigest(),
        "dataset_sha256": cfg["dataset"]["sha256"],
        "engine_commit": cfg["engine"]["commit"],
        "judge": {"route": args.judge, "model": judge_model, "passes": JUDGE_PASSES,
                  "prompt_hash": prompt_hash("judge.md")},
        "conversations": covered,
        "questions_expected": len(expected),
        "questions_answered": sum(1 for q in expected if q.question_id in answers),
        "aggregate": aggregate(rows),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n",
                                      encoding="utf-8", newline="\n")
    agg = summary["aggregate"][args.system]
    print(f"\n{args.system}: {summary['questions_answered']}/{len(expected)} answered")
    for name, b in [("overall", agg["overall"]),
                    ("excluding adversarial", agg["overall_excl_adversarial"]),
                    *sorted(agg["categories"].items())]:
        lo, hi = b["wilson_95"]
        print(f"  {name:24s} {100 * b['accuracy']:5.1f}%  [{100 * lo:.0f} to {100 * hi:.0f}]  "
              f"{b['correct']}/{b['n']}")
    print(f"\nwritten to {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="grade.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("answers", type=pathlib.Path)
    ap.add_argument("--system", required=True, help="a name for the system being graded")
    ap.add_argument("--judge", default="claude", choices=("claude", "gemini"))
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--out", type=pathlib.Path, default=None)
    args = ap.parse_args()
    if os.environ.get("BENCHKIT_INNER") != "1":
        return _outer(sys.argv[1:])
    return _inner(args)


if __name__ == "__main__":
    sys.exit(main())
