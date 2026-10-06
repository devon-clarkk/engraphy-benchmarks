"""The pinned configuration is complete and self-consistent."""

from __future__ import annotations

import re

from benchkit import ROOT, load_config

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
    """`llm-conversational:search_only[:k=N]` expands to the harness's arm id with
    the default confirm policy, and a width other than the shipped 10 as a `/kN`
    suffix. A config naming one and recording the other would publish a result
    under the wrong label."""
    extractor_pack, strategy, *options = CFG["run"]["arm"].split(":")
    width = dict(o.split("=", 1) for o in options).get("k", "10")
    suffix = "" if width == "10" else f"/k{width}"
    assert CFG["run"]["arm_id"] == f"{extractor_pack}/{strategy}/always_distinct{suffix}"


def test_every_role_has_a_model_and_the_judge_is_best_of_three():
    for role in ("extractor", "reader", "adjudicator", "judge"):
        assert CFG["models"][role]
    assert CFG["models"]["judge_passes"] == 3


def test_the_embedder_is_pinned_to_a_revision():
    assert re.fullmatch(r"[0-9a-f]{40}", CFG["embedder"]["revision"])
    assert CFG["embedder"]["profile"] == "onnx-fp32"


def test_the_settling_run_is_pinned_and_covers_the_whole_suite():
    """The settling config pins a full commit, covers all ten conversations at the
    agreed width, and asks for repeated runs. No `hold`, so it is runnable."""
    nxt = load_config(ROOT / "config" / "locomo-next.json")
    assert "hold" not in nxt
    assert re.fullmatch(r"[0-9a-f]{40}", nxt["engine"]["commit"])
    assert nxt["run"]["arm"].endswith(":k=25") and nxt["run"]["arm_id"].endswith("/k25")
    assert nxt["run"]["runs"] >= 2
    # The headline runs on the split no lever was tuned on, and the two splits
    # together are the whole suite with nothing counted twice.
    held, seen = nxt["split"]["held_out"], nxt["split"]["seen"]
    assert nxt["run"]["haystacks"] == held
    assert not set(held) & set(seen) and len(held) + len(seen) == 10
    assert nxt["dataset"] == CFG["dataset"]


def test_the_next_run_measures_the_promoted_extraction_prompt():
    """The config must name the engine that is actually being measured. The
    wider prompt entered the default on 2026-10-02, so a config still naming
    `llm` would publish a configuration nobody ran."""
    nxt = load_config(ROOT / "config" / "locomo-next.json")
    assert nxt["run"]["arm"].startswith("llm_wide-")
    assert nxt["run"]["arm_id"].startswith("llm_wide-")
    # Run A also carries the shipped prompt, so the lever is measured out of sample.
    assert any(a.startswith("llm-") for a in nxt["run"]["arms_in_run_a"])
    assert nxt["run"]["arm"] in nxt["run"]["arms_in_run_a"]
