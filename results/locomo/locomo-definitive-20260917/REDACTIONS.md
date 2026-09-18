# What is committed, and what is withheld

Every figure in this directory recomputes from the committed files alone:

    python scripts/verify_definitive.py

## Committed

| file | contents |
|---|---|
| `results.jsonl` | all 500 questions: id, category, the reader's answer, the strict verdict and its best-of-3 tally, which mechanism graded it, models, timings, evidence ids, failure attribution, support fractions, and the sha256 and size of the retrieval envelope the reader saw |
| `ingest.jsonl` | per-conversation write statistics: memories extracted, stored, and every refusal by class with the engine's message |
| `manifest.json` | the harness manifest: engine commit, configuration, prompt and pack hashes, thresholds, models, judge calibration, aggregates |
| `provenance.json`, `config.json` | host, runtime and database versions; the configuration the run used |
| `reference/results.jsonl` | all 389 non-adversarial questions under the reference harness conventions: the reference reader's final answer and the reference judge's verdict |
| `reference/manifest.json` | the conventions reproduced, every difference from the reference harness, and the vendored prompt hashes |
| `reference/validity_controls.jsonl` | control A (Engraphy's strict judge on all 346 accepted reference answers) and control B (60 deliberately mismatched answers graded by both judges), one row per judge call |
| `reference/evidence_recall.jsonl` | per question, the share of its LoCoMo evidence turns present in the retrieved memory |
| `reference/adjustment.json`, `reference/reference_only_ids.json` | the confabulation adjustment by category, and the questions only the reference rules accept |
| `reference/validity_controls.py` | the script that produced the controls |

## Withheld, and why

LoCoMo is CC BY-NC 4.0 and is distributed by its authors. These fields reproduce its
text, so they are not committed:

| withheld | why | how to restore or check it |
|---|---|---|
| question text and gold answers | dataset text | `scripts/rejoin.py` joins them back from your own copy on `question_id` |
| retrieved memory (`context`, `envelopes.jsonl`) | extracted memories quote the conversation verbatim | the envelope sha256 in each row confirms a rerun handed the reader identical memory |
| the reader's `CHECK:` line and the reference reader's step-by-step working | both quote retrieved memory | only the final answer is graded, and it is committed |
| judge reasoning | it restates the gold answer | the verdict and, for the strict judge, the best-of-3 tally are committed |
| `*_samples` lists in the ingest statistics | extracted memory text | replaced by their counts; write-refusal samples keep the engine's message |
| `calibration_to_label.jsonl`, `failures.md`, `report.md` | question and gold text | the calibration result is in `manifest.json` |

A leak guard checked every committed file against every LoCoMo question: none is
quoted. Two further checks are disclosed here. Some committed answers match their gold
answer word for word (14 strict, 21 reference), because they are correct. One reference
answer (`conv-30:q75`) quotes two lines of the conversation, as the system's recall of what
was said.
