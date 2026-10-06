# What is committed, and what is withheld

Run A of the settling measurement: the combined engine (search width 25 with the
wider extraction prompt) and the shipped extraction prompt as a second arm on one
ingest, over the seven held-out LoCoMo conversations. Strict convention in this
directory, matched convention in `reference/`.

Engine `aa7daa2b9c5f190ee3f10de5b9bf4cbaee44e5a6`, branch `bench/settle-20260930`.

## Committed

| file | contents |
|---|---|
| `results.jsonl` | all 1,486 questions on each of the two arms, 2,972 rows: id, category, the reader's answer, the strict verdict and its best-of-3 tally, which mechanism graded it, models, timings, evidence ids, failure attribution, support fractions, and the sha256 and size of the retrieval envelope the reader saw |
| `reference/results.jsonl` | all 1,151 non-adversarial questions under the matched conventions: the reference reader's final answer and the reference judge's verdict |
| `reference/manifest.json` | the conventions reproduced, every difference from the reference harness, the vendored prompt hashes, and the per-conversation reference dates |
| `arm-compare.json` | the two arms as paired per-question outcomes: accuracy overall and by category, the adversarial rate, discordant counts and exact McNemar p values |
| `retrieval-isolation.txt` | evidence recall, all-evidence-held and context size for seven retrieval arms over this run's store, with no model in the loop |
| `ingest.jsonl` | per-conversation write statistics for all 14 ingests: memories extracted and stored, dedup band rates, edges, and every refusal by class with the engine's message |
| `manifest.json` | engine commit, configuration, pack and prompt hashes including `extract_prompts`, which records the prompt each arm loaded by name and hash, thresholds, models and aggregates |
| `PROVENANCE.md` | host, runtime and database versions |

Every figure in `analysis/2026-10-06-locomo-run-a-consolidated-report.md` and in
`WEBSITE-FIGURES.md` recomputes from these files alone:

    python scripts/consolidate.py results/locomo/locomo-settle-a
    python ../engraphy-bench-settle/scripts/arm_compare.py \
        results/locomo/locomo-settle-a/results.jsonl

## Withheld, and why

LoCoMo is CC BY-NC 4.0 and is distributed by its authors. These reproduce its
text, so they are not committed, on the same policy as
`locomo-definitive-20260917`:

| withheld | why | how to restore or check it |
|---|---|---|
| question text and gold answers | dataset text | `scripts/rejoin.py` joins them back from your own copy on `question_id` |
| retrieved memory (`context`, `envelopes.jsonl`, and the replay envelope files) | extracted memories quote the conversation verbatim | the envelope sha256 in each row confirms a rerun handed the reader identical memory |
| the reader's `CHECK:` line and the reference reader's step-by-step working | both quote retrieved memory | only the final answer is graded, and it is committed |
| judge reasoning | it restates the gold answer | the verdict and, for the strict judge, the best-of-3 tally are committed |
| `*_samples` lists in the ingest statistics | extracted memory text | replaced by their counts; write-refusal samples keep the engine's message |
| `report.md`, `failures.md` | question and gold text | every figure recomputes from `results.jsonl` with the commands above |

Written by `scripts/redact_run.py` and `benchkit.redact.redact_offline_pass`,
which checked every committed file against every LoCoMo question: none is quoted.

The replay envelope files are also withheld for size: the seven arms come to
about 320 MB. They rebuild from this run's store with
`bench.completeness_recall`, and `retrieval-isolation.txt` carries the numbers
they produced.
