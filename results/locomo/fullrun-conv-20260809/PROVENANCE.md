# Provenance: `fullrun-conv-20260809`

Produced on the Engraphy development branch `bench/full-run` at `631e7be`, which is not in the public repository, against schema 0023. The prompts, reader skill, pack, dataset, arm, models and judge match `config/locomo.json`. The embedder ran nomic-embed-text-v1.5 through sentence-transformers rather than ONNX Runtime; the engine's test suite asserts the two produce the same vectors to float noise. The judge calibration phase did not run on this run, and host and runtime were not captured. See METHODOLOGY.md, which figure comes from which engine.

## Result

Arm `llm-conversational/search_only/always_distinct`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **67.1% [62 to 72] (261/389)** |
| overall, all five categories | 71.6% [67 to 75] (358/500) |
| adversarial | 87.4% [80 to 92] (97/111) |
| multi-hop | 56.2% [45 to 67] (45/80) |
| open-domain-knowledge | 57.7% [39 to 74] (15/26) |
| single-hop | 68.5% [61 to 75] (128/187) |
| temporal-reasoning | 76.0% [67 to 83] (73/96) |

Judge instability, one pass against another on a sample: not recorded.
Write-yield at ingest: 99.4% (346 of 348 extracted memories stored).

## What ran

| | |
|---|---|
| run date | 2026-08-09T02:34:29.283736+00:00 |
| engine commit | `631e7be7b23ed73c8059c8091c76ed8b881538f6` |
| engine branch | `bench/full-run` |
| engine tree dirty | False |
| dataset | `locomo10.json` `sha256:79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`, 1986 questions in the file |
| conversations | `conv-26`, `conv-30`, `conv-49` |
| extractor | `claude-opus-4-8` via claude-cli |
| reader | `claude-opus-4-8` via claude-cli |
| judge | `claude-sonnet-5` via claude-cli, provider `claude` |
| reader stance | `grounded` |
| embedding model | `nomic-ai/nomic-embed-text-v1.5` at `e9b6763023c676ca8431644204f50c2b100d9aab` |
| band thresholds | {"t_high": 0.95, "t_low": 0.8, "resonance.floor": 0.75} |
| prompt hashes | `extract.md` sha256:b7fdf557f7f60a9c, `judge.md` sha256:947bebcd5375e93e, `adjudicate.md` sha256:740151c30787a630 |
| models that served | judge: `claude-sonnet-5`; reader: `claude-haiku-4-5-20251001`, `claude-opus-4-8` (the CLI reports every model that ran in a call, including one it runs for its own internal work, so a role can list two) |

## Where it ran

Host and runtime were not captured for this run.

## Files

- `manifest.json`: the harness manifest, with extracted-memory text removed from its ingest samples.
- `results.jsonl`: one row per question, keyed by `question_id`, with the verdict, the best-of-3 tally and the system's answer. No question text, gold answers or conversation text; restore them from your own copy with `scripts/rejoin.py`.
- `ingest.jsonl`: per-conversation write statistics, including every class of write refusal and the engine's message for it.
