"""The matched-convention figure in the committable result: redaction, the
reproduce command, and the rendered provenance."""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import render_provenance  # noqa: E402

import reproduce  # noqa: E402
from benchkit import redact  # noqa: E402


def test_reader_working_and_replay_fields_are_dropped():
    row = {"question_id": "conv-26:q0", "answer": "7 May 2023", "correct": True,
           "reader_check": "Caroline; support group; 'Caroline attended...'",
           "reader_output": "Step 1: SCAN ALL MEMORIES ... ANSWER: 7 May 2023",
           "source_answer": "INSUFFICIENT", "graded_by": "reference_judge",
           "reason": "The generated answer states 7 May 2023, matching the gold."}
    out = redact.redact_row(row)
    assert {"reader_check", "reader_output", "source_answer"}.isdisjoint(out)
    assert out["answer"] == "7 May 2023" and out["reason"] == ""


def test_an_offline_pass_publishes_its_rows_and_manifest_only(tmp_path):
    src = tmp_path / "run" / "reference"
    src.mkdir(parents=True)
    (src / "results.jsonl").write_text(json.dumps(
        {"question_id": "conv-26:q0", "question_text": "Q?", "answer": "a",
         "reader_output": "long"}) + "\n", encoding="utf-8")
    (src / "manifest.json").write_text(json.dumps({"conventions": {"label": "x"}}),
                                       encoding="utf-8")
    (src / "answers.jsonl").write_text("{}\n", encoding="utf-8")
    written = redact.redact_offline_pass(src, tmp_path / "out")
    assert sorted(written) == ["manifest.json", "results.jsonl"]
    row = json.loads((tmp_path / "out" / "results.jsonl").read_text(encoding="utf-8"))
    assert row == {"question_id": "conv-26:q0", "answer": "a"}


def test_reference_command_is_supervised_and_follows_the_config():
    cfg = {"run": {"concurrency": 3, "judge_concurrency": 4},
           "conventions": {"reference": {"judge_passes": 1}}}
    py = pathlib.Path("py")
    cmd = reproduce.reference_command(cfg, py, "r1", supervised=True)
    assert cmd[:3] == ["py", "-m", "bench.supervise"]
    assert "runs/r1/reference" in cmd and cmd[cmd.index("--judge-passes") + 1] == "1"
    assert reproduce.reference_command({"run": {}}, py, "r1", supervised=True) == []


def test_provenance_renders_the_second_figure_beside_the_first(tmp_path):
    bucket = {"n": 389, "correct": 300, "accuracy": 0.7712, "wilson_95": [0.727, 0.81]}
    (tmp_path / "manifest.json").write_text(json.dumps(
        {"run_id": "r1", "aggregate": {"arm": {"overall_excl_adversarial": bucket,
                                               "overall": bucket, "categories": {}}}}),
        encoding="utf-8")
    (tmp_path / "reference").mkdir()
    (tmp_path / "reference" / "manifest.json").write_text(json.dumps({
        "aggregate": {"arm/reference-conventions": {
            "overall_excl_adversarial": bucket, "categories": {"single-hop": bucket}}},
        "conventions": {"label": "measured under the reference harness conventions, "
                                 "for comparability",
                        "source": {"repository": "https://github.com/mem0ai/memory-benchmarks",
                                   "commit": "4b61c5d31b9c", "license": "Apache-2.0"},
                        "reproduced": ["judge prompt verbatim"],
                        "differences": ["memories are Engraphy's"],
                        "prompts": {"judge": {"path": "bench/prompts/reference/judge.md",
                                              "sha256": "sha256:d248"}}},
        "role_models": {"reader": {"model": "claude-opus-4-8"},
                        "judge": {"model": "claude-sonnet-5"}}}), encoding="utf-8")
    (tmp_path / "reference" / "results.jsonl").write_text("{}\n", encoding="utf-8")
    text = render_provenance.render(tmp_path)
    assert "## Under the reference harness conventions" in text
    assert "77.1% [73 to 81] (300/389)" in text and "memories are Engraphy's" in text
    assert text.index("## Result") < text.index("## Under the reference harness conventions")
    assert "`reference/`" in text
