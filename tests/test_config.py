"""The pinned configuration is complete and self-consistent."""

from __future__ import annotations

import re

from benchkit import load_config

CFG = load_config()


def test_the_engine_is_pinned_to_a_full_commit():
    assert re.fullmatch(r"[0-9a-f]{40}", CFG["engine"]["commit"])
    assert CFG["engine"]["repository"].startswith("https://github.com/")


def test_the_dataset_is_pinned_by_digest_and_size():
    assert re.fullmatch(r"[0-9a-f]{64}", CFG["dataset"]["sha256"])
    assert CFG["dataset"]["bytes"] == 2805274
    assert CFG["dataset"]["license"] == "CC BY-NC 4.0"
    assert CFG["dataset"]["url"].startswith("https://raw.githubusercontent.com/snap-research/locomo/")


def test_the_arm_and_its_id_agree():
    """`llm-conversational:search_only` expands to the harness's arm id with the
    default confirm policy. A config naming one and recording the other would
    publish a result under the wrong label."""
    extractor_pack, strategy = CFG["run"]["arm"].split(":")
    assert CFG["run"]["arm_id"] == f"{extractor_pack}/{strategy}/always_distinct"


def test_every_role_has_a_model_and_the_judge_is_best_of_three():
    for role in ("extractor", "reader", "adjudicator", "judge"):
        assert CFG["models"][role]
    assert CFG["models"]["judge_passes"] == 3


def test_the_embedder_is_pinned_to_a_revision():
    assert re.fullmatch(r"[0-9a-f]{40}", CFG["embedder"]["revision"])
    assert CFG["embedder"]["profile"] == "onnx-fp32"
