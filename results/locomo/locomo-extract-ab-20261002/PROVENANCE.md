# Provenance: `extract-ab-seen`

Seen-split extraction A/B: three stores (llm, llm_wide, and a second llm as the replicate floor), store coverage with no model in the loop, the pre-registered gate, then answers and judging on both arms paired per question.

## Result

Arm `llm-conversational/search_only/always_distinct/k25`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **69.2% [64 to 74] (269/389)** |
| overall, all five categories | 73.4% [69 to 77] (367/500) |
| adversarial | 88.3% [81 to 93] (98/111) |
| multi-hop | 57.5% [47 to 68] (46/80) |
| open-domain-knowledge | 69.2% [50 to 84] (18/26) |
| single-hop | 69.5% [63 to 76] (130/187) |
| temporal-reasoning | 78.1% [69 to 85] (75/96) |

Arm `llm_wide-conversational/search_only/always_distinct/k25`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **76.6% [72 to 81] (298/389)** |
| overall, all five categories | 79.2% [75 to 83] (396/500) |
| adversarial | 88.3% [81 to 93] (98/111) |
| multi-hop | 61.3% [50 to 71] (49/80) |
| open-domain-knowledge | 76.9% [58 to 89] (20/26) |
| single-hop | 78.6% [72 to 84] (147/187) |
| temporal-reasoning | 85.4% [77 to 91] (82/96) |

Per-pass judge instability, two single judge passes compared on a sample: not recorded. The best-of-3 majority verdict changes less often than a single pass.
Write-yield at ingest: 99.8% (849 of 851 extracted memories stored).

## What ran

| | |
|---|---|
| run date | 2026-10-01T14:45:58.138107+00:00 |
| engine commit | `d696b6ed5d794655d50929c89aeb2fa22082c42e` |
| engine branch | `bench/settle-20260930` |
| engine tree dirty | False |
| dataset | `locomo10.json` `sha256:79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`, 1986 questions in the file |
| conversations | `conv-26`, `conv-30`, `conv-49` |
| extractor | `claude-opus-4-8` via claude-cli |
| reader | `claude-opus-4-8` via claude-cli |
| judge | `claude-sonnet-5` via claude-cli, provider `claude` |
| reader stance | `grounded` |
| embedding model | `nomic-ai/nomic-embed-text-v1.5` at `e9b6763023c676ca8431644204f50c2b100d9aab` |
| band thresholds | {"t_high": 0.95, "t_low": 0.8, "resonance.floor": 0.75} |
| prompt hashes | `extract.md` sha256:b7fdf557f7f60a9c, `extract-wide.md` sha256:2f3fa4c9e6c1a457, `judge.md` sha256:947bebcd5375e93e, `adjudicate.md` sha256:740151c30787a630 |
| models that served | judge: `claude-sonnet-5`; reader: `claude-opus-4-8` |

## Where it ran

Host and runtime were not captured for this run.

## Files

- `manifest.json`: the harness manifest, with extracted-memory text removed from its ingest samples.
- `results.jsonl`: one row per question, keyed by `question_id`, with the verdict, the best-of-3 tally and the system's answer. No question text, gold answers or conversation text; restore them from your own copy with `scripts/rejoin.py`.
- `ingest.jsonl`: per-conversation write statistics, including every class of write refusal and the engine's message for it.
