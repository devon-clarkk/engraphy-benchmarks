# What is committed, and what is withheld

Run B of the settling measurement: an independent second run of the combined
engine (search width 25 with the wider extraction prompt) over the seven held-out
LoCoMo conversations, ingest included, so that run A and run B together give the
run-to-run spread. Strict convention in this directory, matched convention in
`reference/`.

Engine `aa7daa2b9c5f190ee3f10de5b9bf4cbaee44e5a6`, branch `bench/settle-20260930`.
One arm, `llm_wide-conversational/search_only/always_distinct/k25`: run A carried
a second arm for the extraction comparison, and run B's job is the spread of the
shipped configuration.

## Committed

| file | contents |
|---|---|
| `results.jsonl` | all 1,486 questions: id, category, the reader's answer, the strict verdict and its best-of-3 tally, which mechanism graded it, models, timings, evidence ids, failure attribution, support fractions, and the sha256 and size of the retrieval envelope the reader saw |
| `reference/results.jsonl` | all 1,151 non-adversarial questions under the matched conventions: the reference reader's final answer and the reference judge's verdict |
| `reference/manifest.json` | the conventions reproduced, every difference from the reference harness, the vendored prompt hashes, and the per-conversation reference dates |
| `ingest.jsonl` | per-conversation write statistics for all 7 ingests: memories extracted and stored, dedup band rates, edges, and every refusal by class with the engine's message |
| `manifest.json` | engine commit, configuration, pack and prompt hashes including `extract_prompts`, thresholds, models and aggregates |
| `PROVENANCE.md` | engine commit and branch, dataset hash, models, prompt hashes and the matched-pass conventions |

Both runs' figures, and the spread between them, recompute from the committed
copies alone:

    python scripts/consolidate.py results/locomo/locomo-settle-a \
                                  results/locomo/locomo-settle-b

## Withheld, and why

LoCoMo is CC BY-NC 4.0 and is distributed by its authors. These reproduce its
text, so they are not committed, on the same policy as `locomo-settle-a`:

| withheld | why | how to restore or check it |
|---|---|---|
| question text and gold answers | dataset text | `scripts/rejoin.py` joins them back from your own copy on `question_id` |
| retrieved memory (`context`, `envelopes.jsonl`) | extracted memories quote the conversation verbatim | the envelope sha256 in each row confirms a rerun handed the reader identical memory |
| the reader's `CHECK:` line and the reference reader's step-by-step working | both quote retrieved memory | only the final answer is graded, and it is committed |
| judge reasoning | it restates the gold answer | the verdict and, for the strict judge, the best-of-3 tally are committed |
| `*_samples` lists in the ingest statistics | extracted memory text | replaced by their counts; write-refusal samples keep the engine's message |
| `report.md`, `failures.md` | question and gold text | every figure recomputes from `results.jsonl` with the command above |

Written by `scripts/redact_run.py` and `benchkit.redact.redact_offline_pass`,
which checked every committed file against every LoCoMo question: none is quoted.
