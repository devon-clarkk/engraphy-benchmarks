# Provenance: `fullrun-conv-20260916`

Produced from the public repository `EngraphyLabs/engraphy` at `67dd41a` (branch `fix/pin-onnxruntime`, which pins onnxruntime ~=1.29.0; schema 0024), in a clean checkout, with the configuration in `config.json`: the default embedding profile `onnx-fp32` on ONNX Runtime 1.29.0, and the engine's default phases, concurrency and calibration sample, which are the values the configuration pins. This is the engine `reproduce.py` runs. Retrieval is the engine's `search_only` default, 10 results at full detail, the value the 2026-08-09 manifest records under `retrieval_configs`; this commit's manifest does not carry that field. All 500 questions were answered and graded with no reader or judge error, as `results.jsonl` shows row by row. The run paused once at a Claude usage limit during answering and resumed from its checkpoint under the supervisor. See METHODOLOGY.md, which figure comes from which engine.

## Result

Arm `llm-conversational/search_only/always_distinct`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **60.2% [55 to 65] (234/389)** |
| overall, all five categories | 63.2% [59 to 67] (316/500) |
| adversarial | 73.9% [65 to 81] (82/111) |
| multi-hop | 43.8% [33 to 55] (35/80) |
| open-domain-knowledge | 57.7% [39 to 74] (15/26) |
| single-hop | 63.6% [57 to 70] (119/187) |
| temporal-reasoning | 67.7% [58 to 76] (65/96) |

Per-pass judge instability, two single judge passes compared on a sample: 0.0% (0 of 40 items graded twice). The best-of-3 majority verdict changes less often than a single pass.
Write-yield at ingest: 85.7% (269 of 314 extracted memories stored).

## What ran

| | |
|---|---|
| run date | 2026-09-15T16:51:27.247141+00:00 |
| engine commit | `67dd41acf9e5bcd82884ffd8535d20bdd5020021` |
| engine branch | `fix/pin-onnxruntime` |
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
| models that served | judge: `claude-sonnet-5`; reader: `claude-opus-4-8` |
| embedding profile | `onnx-fp32`, onnxruntime 1.29.0 |

## Where it ran

| | |
|---|---|
| CPU | 11th Gen Intel(R) Core(TM) i5-11600K @ 3.90GHz, 12 logical |
| memory | 15.8 GB |
| OS | Windows 11 (10.0.26100) |
| Python | 3.14.3 |
| packages | onnxruntime 1.29.0, tokenizers 0.22.2, numpy 2.4.4, psycopg 3.3.4, psycopg-pool 3.3.1, huggingface-hub 0.36.2, pyyaml 6.0.3 |
| Postgres | 16.14 (Debian 16.14-1.pgdg12+1), pgvector 0.8.5 |
| Docker | 28.3.0 |
| Claude Code CLI | 2.1.252 (Claude Code) |

## Files

- `manifest.json`: the harness manifest, with extracted-memory text removed from its ingest samples.
- `results.jsonl`: one row per question, keyed by `question_id`, with the verdict, the best-of-3 tally and the system's answer. No question text, gold answers or conversation text; restore them from your own copy with `scripts/rejoin.py`.
- `ingest.jsonl`: per-conversation write statistics, including every class of write refusal and the engine's message for it.
- `provenance.json`: host, runtime and database versions.
- `config.json`: the configuration this run was produced with.
