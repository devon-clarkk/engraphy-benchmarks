"""Nothing the dataset supplies survives into a committed artifact."""

from __future__ import annotations

import json
import pathlib

from benchkit import dataset, redact

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "tiny_locomo.json"

ROW = {
    "arm": "llm-conversational/search_only/always_distinct",
    "question_id": "tiny-1:q0",
    "category": "single-hop",
    "question_text": "When does Ada repaint the lighthouse each year?",
    "gold_answer": "every spring",
    "context": [{"title": "Ada repaints the lighthouse", "body": "every spring"}],
    "gold_in_context": {"supported": True, "fraction": 1.0, "matched": ["spring"], "missing": []},
    "gold_in_store": {"supported": True, "fraction": 1.0, "matched": ["spring"], "missing": []},
    "answer": "Every spring.",
    "correct": True,
    "reason": "[best-of-3: 3 correct / 0 wrong] The candidate matches the gold, every spring.",
    "graded_by": "judge",
    "envelope_sha256": "ab" * 32,
    "envelope_bytes": 1234,
}


def test_dataset_text_is_dropped_and_audit_fields_kept():
    out = redact.redact_row(ROW)
    for gone in ("question_text", "gold_answer", "context"):
        assert gone not in out
    for kept in ("question_id", "category", "answer", "correct", "graded_by",
                 "envelope_sha256", "envelope_bytes"):
        assert out[kept] == ROW[kept]


def test_the_judge_reason_keeps_only_the_tally():
    """The judge's prose restates the gold answer; the tally is the harness's own."""
    assert redact.redact_row(ROW)["reason"] == "[best-of-3: 3 correct / 0 wrong]"


def test_the_abstention_rule_reason_is_kept_whole():
    row = {**ROW, "graded_by": "abstention_rule", "reason": "declined, as the question requires"}
    assert redact.redact_row(row)["reason"] == "declined, as the question requires"


def test_support_fractions_survive_without_their_words():
    out = redact.redact_row(ROW)
    assert out["gold_in_context"] == {"supported": True, "fraction": 1.0}
    assert out["gold_in_store"] == {"supported": True, "fraction": 1.0}


def test_write_refusals_keep_the_engine_message_and_lose_the_title():
    """The refusal is the evidence behind a write-yield figure, so its class and
    the engine's message survive; the title is conversation text and does not."""
    sample = {"error": "CheckViolation",
              "detail": "attrs.as_of must be a date\nCONTEXT:  PL/pgSQL function ...",
              "node_type": "fact", "title_len": 42, "body_len": 368, "attr_keys": ["as_of"],
              "title": "Ada repaints the lighthouse every spring"}
    out = redact.redact_samples({"write_error_samples": [sample]})["write_error_samples"]
    assert out == [{"error": "CheckViolation", "detail": "attrs.as_of must be a date",
                    "node_type": "fact", "title_len": 42, "body_len": 368,
                    "attr_keys": ["as_of"]}]


def test_other_sample_lists_become_counts_at_any_depth():
    ingest = {"haystack_id": "tiny-1", "drafts": 3,
              "nested": {"extraction_error_samples": [{"error": "model said: Ada ..."}]}}
    assert redact.redact_samples(ingest) == {
        "haystack_id": "tiny-1", "drafts": 3, "nested": {"extraction_error_samples": 1},
    }


def test_redact_run_writes_only_committable_files(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    (run / "results.jsonl").write_text(json.dumps(ROW) + "\n", encoding="utf-8")
    refusal = {"write_error_samples": [{"error": "CheckViolation", "title": "x"}]}
    (run / "ingest.jsonl").write_text(json.dumps(refusal) + "\n", encoding="utf-8")
    (run / "manifest.json").write_text(json.dumps({"ingest": [{"x_samples": [1, 2]}]}),
                                       encoding="utf-8")
    (run / "answers.jsonl").write_text("{}\n", encoding="utf-8")

    dest = tmp_path / "out"
    redact.redact_run(run, dest)
    names = sorted(p.name for p in dest.iterdir())
    assert names == ["ingest.jsonl", "manifest.json", "results.jsonl"]
    text = (dest / "results.jsonl").read_text(encoding="utf-8")
    assert ROW["question_text"] not in text
    assert ROW["gold_answer"] not in text.lower().replace("every spring.", "")
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    assert manifest == {"ingest": [{"x_samples": 2}]}
    ingest = json.loads((dest / "ingest.jsonl").read_text(encoding="utf-8"))
    assert ingest == {"write_error_samples": [{"error": "CheckViolation"}]}


def test_the_report_guard_finds_a_quoted_question():
    index = dataset.question_index(FIXTURE)
    report = "Worst miss: Which cliff is the lighthouse Ada repaints standing on? (multi-hop)"
    assert redact.leaks(report, index) == ["tiny-1:q1"]
    assert redact.leaks("accuracy table only", index) == []
