"""Validity controls for the matched-convention figure. Checkpointed per call.

A. The strict judge (one pass) on every reference answer the reference judge
   accepted: separates what the reference reader got right under Engraphy's own
   rubric from what only the partial-credit rules accept.
B. Mismatched answers: 60 accepted questions each paired with the reference
   answer to a different question from the same conversation, graded by both
   judges. Every pair is wrong by construction; acceptances measure leniency.

Resume by running again; finished calls are skipped.
"""
import concurrent.futures as cf
import hashlib
import json
import pathlib
import sys

from bench import offline
from bench.core import run as harness
from bench.core.providers import ClaudeCLIClient, QuotaExhausted
from bench.core.reference import ReferenceJudge

RUN = pathlib.Path("runs/locomo-definitive-20260917")
OUT = RUN / "reference" / "validity_controls.jsonl"
src = offline.load_source(RUN)
ref = {json.loads(line)["question_id"]: json.loads(line)
       for line in open(RUN / "reference" / "results.jsonl", encoding="utf-8")}
done = set()
if OUT.exists():
    for line in OUT.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        done.add((r["control"], r["key"]))

jobs = []
for qid, r in sorted(ref.items()):
    if r["correct"]:
        jobs.append(("A_strict_on_reference_answer", qid, qid, r["answer"], ("strict",)))
by_conv: dict[str, list] = {}
for r in ref.values():
    by_conv.setdefault(r["haystack_id"], []).append(r)
pool = sorted((r for r in ref.values() if r["correct"]),
              key=lambda r: hashlib.sha256(("ctl:" + r["question_id"]).encode()).hexdigest())[:60]
for r in pool:
    other = sorted((o for o in by_conv[r["haystack_id"]] if o["question_id"] != r["question_id"]),
                   key=lambda o: hashlib.sha256((r["question_id"] + o["question_id"]).encode())
                   .hexdigest())[0]
    jobs.append(("B_mismatched", f"{r['question_id']}<-{other['question_id']}", r["question_id"],
                 other["answer"], ("reference", "strict")))
jobs = [j for j in jobs if (j[0], j[1]) not in done]
print(f"{len(jobs)} control jobs to run", flush=True)


def run(job):
    control, key, qid, answer, judges = job
    q = src.questions[qid]
    out = {"control": control, "key": key, "question_id": qid, "category": q.category}
    for j in judges:
        if j == "reference":
            v = ReferenceJudge(ClaudeCLIClient(model=harness.CLAUDE_JUDGE_MODEL)).grade(q, answer)
        else:
            v = harness._build_judge("claude").grade(q, answer)
        if v.graded_by == "judge_error":
            return None
        out[j] = v.correct
    return out


stopped = False
with cf.ThreadPoolExecutor(4) as ex, OUT.open("a", encoding="utf-8") as fh:
    futs = [ex.submit(run, j) for j in jobs]
    n = 0
    for f in cf.as_completed(futs):
        try:
            row = f.result()
        except QuotaExhausted as exc:
            if not stopped:
                print(f"[stop] usage limit: {str(exc)[:120]}", flush=True)
            stopped = True
            for other in futs:
                other.cancel()
            continue
        if row:
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            n += 1
            if n % 50 == 0:
                print(f"  {n} done", flush=True)
print("STOPPED" if stopped else "CONTROLS COMPLETE", flush=True)
sys.exit(1 if stopped else 0)
