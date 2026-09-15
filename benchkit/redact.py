"""Strip LoCoMo-derived text from run artifacts before they are committed.

A harness results row carries the question, the gold answer, and several
kilobytes of retrieved memory built from the conversation. Committing those rows
as they are would republish a substantial part of a CC BY-NC dataset whose
authors distribute it themselves. So the committed rows keep what an audit needs
and drop what the dataset supplies:

kept     ids, category, the system's own answer, the verdict and its best-of-3
         tally, which mechanism graded it, models, timings, payload size and its
         sha256, the failure attribution, and support fractions
dropped  question text, gold answer, retrieved context, matched and missing gold
         terms, judge reasoning (it restates the gold), and every `*_samples`
         list of extracted memory text in the ingest statistics

Anyone holding their own copy of the dataset restores the question and gold with
scripts/rejoin.py, which joins on question_id. The envelope sha256 lets them
confirm a rerun handed the reader byte-identical memory.

Ingest statistics are handled field by field. `write_error_samples` explain why
an extracted memory was not stored, which is the evidence behind a write-yield
figure, so each sample keeps the error class, the first line of the engine's
message, the node type, the attribute keys and the lengths, and loses its title.
Every other `*_samples` list is replaced by its length, because its entries can
carry model output drawn from the conversation.
"""

from __future__ import annotations

import json
import pathlib
import re

DROP_ROW_FIELDS = frozenset({
    "question_text",
    "gold_answer",
    "context",
    "evidence_text",
})

# Support dicts keep their numbers and lose their words.
SUPPORT_FIELDS = ("gold_in_context", "gold_in_store")

_TALLY = re.compile(r"^\[best-of-\d+: \d+ correct / \d+ wrong\]")


def redact_row(row: dict) -> dict:
    out = {k: v for k, v in row.items() if k not in DROP_ROW_FIELDS}
    for key in SUPPORT_FIELDS:
        if isinstance(out.get(key), dict):
            out[key] = {k: v for k, v in out[key].items()
                        if k not in ("matched", "missing")}
    if "reason" in out:
        out["reason"] = _reason_without_gold(out.get("reason") or "", out.get("graded_by"))
    return out


def _reason_without_gold(reason: str, graded_by: str | None) -> str:
    """Keep the tally, which is ours; drop the prose, which quotes the dataset.

    The abstention rule's reasons are fixed strings the harness wrote, with no
    dataset text in them, so they are kept whole.
    """
    if graded_by == "abstention_rule":
        return reason
    m = _TALLY.match(reason)
    return m.group(0) if m else ""


# What a write-refusal sample keeps. `detail` is the engine's own message, cut to
# its first line; the rest are counts, names from the pack, or the error class.
WRITE_ERROR_KEEP = frozenset({"error", "detail", "node_type", "attr_keys",
                              "title_len", "body_len"})


def _write_error_sample(sample: dict) -> dict:
    return {k: (v.split("\n", 1)[0] if k == "detail" and isinstance(v, str) else v)
            for k, v in sample.items() if k in WRITE_ERROR_KEEP}


def redact_samples(obj):
    """Strip conversation text from `*_samples` lists, recursively."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "write_error_samples" and isinstance(v, list):
                out[k] = [_write_error_sample(s) for s in v if isinstance(s, dict)]
            elif k.endswith("_samples") and isinstance(v, list):
                out[k] = len(v)
            else:
                out[k] = redact_samples(v)
        return out
    if isinstance(obj, list):
        return [redact_samples(v) for v in obj]
    return obj


def redact_jsonl(src: pathlib.Path, dest: pathlib.Path, fn) -> int:
    n = 0
    with src.open(encoding="utf-8") as fin, dest.open("w", encoding="utf-8", newline="\n") as fout:
        for line in fin:
            if line.strip():
                fout.write(json.dumps(fn(json.loads(line)), ensure_ascii=False) + "\n")
                n += 1
    return n


def redact_run(run_dir: pathlib.Path, dest: pathlib.Path) -> dict:
    """Write the committable subset of one harness run directory to `dest`."""
    dest.mkdir(parents=True, exist_ok=True)
    written: dict[str, int | str] = {}

    results = run_dir / "results.jsonl"
    if results.exists():
        written["results.jsonl"] = redact_jsonl(results, dest / "results.jsonl", redact_row)

    ingest = run_dir / "ingest.jsonl"
    if ingest.exists():
        written["ingest.jsonl"] = redact_jsonl(ingest, dest / "ingest.jsonl", redact_samples)

    manifest = run_dir / "manifest.json"
    if manifest.exists():
        m = redact_samples(json.loads(manifest.read_text(encoding="utf-8")))
        (dest / "manifest.json").write_text(
            json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        written["manifest.json"] = "redacted"

    return written


def leaks(text: str, index: dict[str, dict], *, min_len: int = 24) -> list[str]:
    """Question texts from the dataset that appear verbatim in `text`.

    A guard for the report files, which are rendered prose rather than rows. Short
    questions are skipped because a short question can collide with ordinary
    words; every LoCoMo question of real length is checked.
    """
    return [qid for qid, q in index.items()
            if len(q["question"]) >= min_len and q["question"] in text]
