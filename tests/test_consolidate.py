"""Consolidation reads one arm, and never pools two into one mean.

Run A of the settling measurement carries the combined engine and the shipped
extraction prompt on one ingest. Pooling them would report a figure midway
between two configurations, which no configuration produced, and the mean is the
headline.
"""

from __future__ import annotations

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("consolidate", ROOT / "scripts" / "consolidate.py")
consolidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consolidate)

WIDE = "llm_wide-conversational/search_only/always_distinct/k25"
CONTROL = "llm-conversational/search_only/always_distinct/k25"
ROWS = [{"arm": WIDE, "question_id": "q1", "correct": True, "category": "single-hop"},
        {"arm": WIDE, "question_id": "q2", "correct": True, "category": "single-hop"},
        {"arm": CONTROL, "question_id": "q1", "correct": False, "category": "single-hop"},
        {"arm": CONTROL, "question_id": "q2", "correct": False, "category": "single-hop"}]


def test_each_arm_is_counted_on_its_own():
    assert consolidate.buckets(consolidate.for_arm(ROWS, WIDE))["single-hop"] == (2, 2)
    assert consolidate.buckets(consolidate.for_arm(ROWS, CONTROL))["single-hop"] == (0, 2)


def test_pooling_the_two_would_report_a_figure_neither_produced():
    """The guard this test exists for: 50% is not either arm's accuracy."""
    assert consolidate.buckets(ROWS)["single-hop"] == (2, 4)


def test_the_reference_pass_suffix_belongs_to_its_arm():
    ref = [{"arm": WIDE + "/reference-conventions", "question_id": "q1", "correct": True,
            "category": "single-hop"}]
    assert len(consolidate.for_arm(ref, WIDE)) == 1
    assert consolidate.for_arm(ref, CONTROL) == []


def test_the_arms_present_are_listed_without_the_suffix():
    assert consolidate.arms_in(ROWS) == sorted([WIDE, CONTROL])


def test_the_default_arm_is_the_combined_engine():
    assert consolidate.DEFAULT_ARM == WIDE
