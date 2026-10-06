# What is committed, and what is withheld

This directory holds the seen-split extraction A/B: the measurement that decided
whether the wider extraction prompt (`llm_wide`) entered the engine. The rule it
was decided against was fixed first, in
`analysis/2026-09-30-settling-run-preregistration.md`, addendum 2026-10-01.

The three stores all came from one engine at commit
`b9a3afc10c42880614ff046b840dee221bd708a9`, on conv-26, conv-30 and conv-49:

| store | extraction prompt | role |
|---|---|---|
| `llm` | `extract.md` | the shipped control |
| `llm_wide` | `extract-wide.md` | the candidate |
| `llm` again, under its own run id | `extract.md` | the replicate, which is the noise floor the candidate had to clear |

## Committed

| file | contents |
|---|---|
| `coverage.json` | store coverage per store, with no model in the loop: whether each question's cited evidence is present in any stored memory of that scope, as a rate, by labelled gap class, and per question as a 0 or 1, plus memories per scope |
| `gate.txt` | the pre-registered gate applied to `coverage.json`: the replicate floor, the lever's gain, the discordant counts, the exact McNemar p value, the store-size change, and the verdict |
| `arm-compare.json` | both arms as paired per-question outcomes: non-adversarial accuracy overall and by category, the adversarial rate, and the exact McNemar p value per slice |
| `results.jsonl` | all 500 questions on each arm: id, category, the reader's answer, the strict verdict and its best-of-3 tally, models, timings, evidence ids, failure attribution, support fractions, and the sha256 and size of the retrieval envelope the reader saw |
| `ingest.jsonl`, `replicate/ingest.jsonl` | per-conversation write statistics for all nine ingests: memories extracted and stored, dedup band rates, edges, and every refusal by class with the engine's message |
| `manifest.json`, `replicate/manifest.json` | engine commit, configuration, pack and prompt hashes including `extract_prompts`, which records the prompt each arm loaded by name and hash, thresholds and models |
| `PROVENANCE.md` | host, runtime and database versions |

`extract_prompts` is what makes the A/B checkable: the run-wide `prompt_hashes`
block lists every prompt in the tree, so it reads the same whichever arm selected
which, and on its own it cannot show that the two arms differed in the thing under
test.

## Withheld, and why

LoCoMo is CC BY-NC 4.0 and is distributed by its authors. These reproduce its
text, so they are not committed, on the same policy as
`locomo-definitive-20260917`:

| withheld | why | how to restore or check it |
|---|---|---|
| question text and gold answers | dataset text | `scripts/rejoin.py` joins them back from your own copy on `question_id` |
| retrieved memory (`context`, `envelopes.jsonl`) | extracted memories quote the conversation verbatim | the envelope sha256 in each row confirms a rerun handed the reader identical memory |
| the reader's `CHECK:` line | it quotes retrieved memory | only the final answer is graded, and it is committed |
| judge reasoning | it restates the gold answer | the verdict and the best-of-3 tally are committed |
| `*_samples` lists in the ingest statistics | extracted memory text | replaced by their counts; write-refusal samples keep the engine's message |
| `report.md`, `failures.md` | question and gold text | every figure recomputes from `results.jsonl` with `scripts/arm_compare.py` |

Written by `scripts/redact_run.py`, which checked every committed file against
every LoCoMo question: none is quoted.

## Recomputing the numbers

    python scripts/arm_compare.py results/locomo/locomo-extract-ab-20261002/results.jsonl
    python ../engraphy-bench-settle/scripts/extraction_gate.py \
        results/locomo/locomo-extract-ab-20261002/coverage.json

Coverage itself is recomputed from a store, not from this directory, so it needs
the ingests rerun; `coverage.json` carries the per-question outcomes it produced
so the gate can be checked without them.
