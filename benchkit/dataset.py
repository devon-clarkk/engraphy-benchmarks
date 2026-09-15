"""LoCoMo: download from the original source, verify, and index.

The dataset is never committed to this repository. LoCoMo is licensed CC BY-NC
4.0 by its authors, and the copy anyone runs should come from them. This module
downloads it from snap-research/locomo, refuses a file whose sha256 differs from
the one every published figure here was produced on, and saves the upstream
licence beside it.

The index functions reproduce the engine loader's question ids exactly
(`{sample_id}:q{j}`, `j` the 0-based position in that conversation's `qa` list),
so committed results that carry only ids can be rejoined with a local copy for
auditing.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.request

CATEGORY_NAMES = {
    1: "multi-hop",
    2: "temporal-reasoning",
    3: "open-domain-knowledge",
    4: "single-hop",
    5: "adversarial",
}
ADVERSARIAL = 5


class DatasetError(RuntimeError):
    """The dataset is missing, or is not the pinned file."""


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(path: pathlib.Path, expected_sha256: str) -> str:
    """Raise unless `path` is the pinned file. Returns the digest."""
    if not path.exists():
        raise DatasetError(f"{path} does not exist; run scripts/fetch_locomo.py")
    got = sha256_of(path)
    if got != expected_sha256:
        raise DatasetError(
            f"{path} has sha256 {got}, not the pinned {expected_sha256}. LoCoMo "
            "circulates in more than one revision, and a figure produced on a "
            "different file is not comparable to one produced on this one."
        )
    return got


def fetch(cfg: dict, dest_dir: pathlib.Path, *, opener=urllib.request.urlopen) -> pathlib.Path:
    """Download the dataset and its licence into `dest_dir`, then verify.

    A file already present and matching the pin is kept as it is, so a resumed
    reproduction does not download it twice.
    """
    ds = cfg["dataset"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    data_path = dest_dir / "locomo10.json"
    licence_path = dest_dir / "locomo10.LICENSE.txt"

    if not (data_path.exists() and sha256_of(data_path) == ds["sha256"]):
        _download(ds["url"], data_path, opener)
    if not licence_path.exists():
        _download(ds["license_url"], licence_path, opener)

    verify(data_path, ds["sha256"])
    return data_path


def _download(url: str, dest: pathlib.Path, opener) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    with opener(url) as resp, tmp.open("wb") as out:
        out.write(resp.read())
    tmp.replace(dest)


def question_index(path: pathlib.Path) -> dict[str, dict]:
    """question_id -> {question, gold, category, abstain_expected, evidence}.

    Mirrors the engine's LoCoMoLoader id scheme and category mapping, including
    reading the adversarial gold from `adversarial_answer`.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for sample in raw:
        sample_id = sample["sample_id"]
        for j, item in enumerate(sample.get("qa") or []):
            cat = int(item["category"])
            abstain = cat == ADVERSARIAL
            gold = (item.get("adversarial_answer", item.get("answer", ""))
                    if abstain else item.get("answer", ""))
            evidence = item.get("evidence") or []
            if isinstance(evidence, str):
                evidence = [evidence]
            out[f"{sample_id}:q{j}"] = {
                "question": str(item.get("question", "")),
                "gold_answer": gold if isinstance(gold, str) else json.dumps(gold),
                "category": CATEGORY_NAMES[cat],
                "abstain_expected": abstain,
                "evidence": [str(e) for e in evidence],
            }
    return out
