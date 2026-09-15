"""Dataset fetch, verification and the question-id scheme.

The fixture is invented text in LoCoMo's shape, not LoCoMo content, so these tests
run without the dataset and without redistributing any of it.
"""

from __future__ import annotations

import io
import pathlib

import pytest

from benchkit import dataset

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "tiny_locomo.json"


def test_ids_follow_the_engine_loader_scheme():
    """`{sample_id}:q{j}`, j 0-based within the conversation. Committed results
    carry only these ids, so a scheme that drifted from the engine's would rejoin
    every row to the wrong question."""
    index = dataset.question_index(FIXTURE)
    assert list(index) == ["tiny-1:q0", "tiny-1:q1", "tiny-1:q2", "tiny-2:q0"]


def test_categories_use_the_published_mapping():
    index = dataset.question_index(FIXTURE)
    assert index["tiny-1:q0"]["category"] == "single-hop"
    assert index["tiny-1:q1"]["category"] == "multi-hop"
    assert index["tiny-1:q2"]["category"] == "adversarial"
    assert index["tiny-2:q0"]["category"] == "temporal-reasoning"


def test_adversarial_gold_comes_from_its_own_key():
    q = dataset.question_index(FIXTURE)["tiny-1:q2"]
    assert q["abstain_expected"] is True
    assert q["gold_answer"] == "not mentioned"


def test_non_string_gold_and_string_evidence_are_normalised():
    index = dataset.question_index(FIXTURE)
    assert index["tiny-2:q0"]["gold_answer"] == "40"
    assert index["tiny-1:q1"]["evidence"] == ["D1:2"]


def test_a_file_that_is_not_the_pin_is_refused(tmp_path):
    other = tmp_path / "locomo10.json"
    other.write_text("[]", encoding="utf-8")
    with pytest.raises(dataset.DatasetError, match="not the pinned"):
        dataset.verify(other, "0" * 64)


def test_a_missing_file_says_how_to_get_it(tmp_path):
    with pytest.raises(dataset.DatasetError, match="fetch_locomo"):
        dataset.verify(tmp_path / "absent.json", "0" * 64)


def test_fetch_downloads_both_files_and_verifies(tmp_path):
    body = FIXTURE.read_bytes()
    served = {"https://example.test/data.json": body,
              "https://example.test/LICENSE": b"CC BY-NC 4.0"}
    calls: list[str] = []

    def opener(url):
        calls.append(url)
        return io.BytesIO(served[url])

    cfg = {"dataset": {"url": "https://example.test/data.json",
                       "license_url": "https://example.test/LICENSE",
                       "sha256": dataset.sha256_of(FIXTURE)}}
    path = dataset.fetch(cfg, tmp_path, opener=opener)
    assert path.read_bytes() == body
    assert (tmp_path / "locomo10.LICENSE.txt").read_bytes() == b"CC BY-NC 4.0"

    # A second fetch keeps the verified file rather than downloading it again.
    calls.clear()
    dataset.fetch(cfg, tmp_path, opener=opener)
    assert calls == []


def test_fetch_refuses_a_download_that_does_not_match(tmp_path):
    def opener(url):
        return io.BytesIO(b"[]")

    cfg = {"dataset": {"url": "u", "license_url": "l", "sha256": "0" * 64}}
    with pytest.raises(dataset.DatasetError):
        dataset.fetch(cfg, tmp_path, opener=opener)
