# Provenance: `locomo-definitive-20260917`

Produced from `devon-clarkk/engraphy` at `3df1a4d` (branch `bench/locomo-conventions-reader-width`): PR #23 head `99b38a5` plus the reference-convention pass, the subject-and-occasion reader check with the `verify` reply contract, and search width 20, chosen by the rule in `analysis/2026-09-16-levers-preregistration.md` before it was measured. Clean checkout, schema 0028, configuration in `config.json`. The run crossed three usage caps and a machine restart and resumed from its checkpoints each time. The figure under the reference harness conventions and its validity controls are in `reference/`; `scripts/verify_definitive.py` recomputes every figure from the committed files. See `REDACTIONS.md` for what is not committed and why.

## Result

Arm `llm-conversational/search_only/always_distinct/k20`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **66.8% [62 to 71] (260/389)** |
| overall, all five categories | 71.8% [68 to 76] (359/500) |
| adversarial | 89.2% [82 to 94] (99/111) |
| multi-hop | 53.8% [43 to 64] (43/80) |
| open-domain-knowledge | 69.2% [50 to 84] (18/26) |
| single-hop | 69.0% [62 to 75] (129/187) |
| temporal-reasoning | 72.9% [63 to 81] (70/96) |

Per-pass judge instability, two single judge passes compared on a sample: 2.5% (1 of 40 items graded twice). The best-of-3 majority verdict changes less often than a single pass.
Write-yield at ingest: 95.2% (318 of 334 extracted memories stored).

## Under the reference harness conventions

Measured measured under the reference harness conventions, for comparability, over the same run: every non-adversarial question read again from the envelope the run saved, under the answer prompt and judge of [https://github.com/mem0ai/memory-benchmarks](https://github.com/mem0ai/memory-benchmarks) at `4b61c5d31b9c` (Apache-2.0). The strict figure above is Engraphy's primary figure.

Arm `llm-conversational/search_only/always_distinct/k20/reference-conventions`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **88.9% [85 to 92] (346/389)** |
| multi-hop | 95.0% [88 to 98] (76/80) |
| open-domain-knowledge | 92.3% [76 to 98] (24/26) |
| single-hop | 85.0% [79 to 89] (159/187) |
| temporal-reasoning | 90.6% [83 to 95] (87/96) |

Reader `claude-opus-4-8`, judge `claude-sonnet-5`.

Reproduced from the reference harness:

- answer prompt verbatim: commit to an answer, never decline; answer taken after the last 'ANSWER:'
- at most 200 memories, oldest first, no ranks or scores
- reference date: the latest session's date string
- judge prompt verbatim, without evidence (the reference default): at least one gold item suffices, dates within 14 days, durations within 50%
- open-domain gold cut at the first semicolon
- categories 1-4 scored; adversarial excluded
- 1 judge pass(es) per answer (the reference uses 1)

Where this differs from the reference harness:

- memories are Engraphy's, from Engraphy's search at the run's retrieval width; the reference retrieves up to 200 from its own store
- each reference memory line carries its session date; Engraphy memories keep dates in their text and attributes and created_at is ingest time, so each line uses the reference's no-date form '(unknown date)'
- reader and judge models are the run's, not the reference defaults
- an Engraphy memory is rendered as one line: title, body and attributes

- prompt `bench/prompts/reference/answer.md`: `sha256:79c9f09bcc8d5e9e8b7e9786af587b02a67d366ab79285fc148b73fd20f6297b`
- prompt `bench/prompts/reference/judge.md`: `sha256:d248e056d993725e28fba8d16ca7081f0b59deae272ef294f3c6b00d48eac02b`
- prompt `bench/prompts/reference/judge_system.md`: `sha256:36c007917faf1ab84516cdca577fb523711a9b993706fbae8ae37806e6f9adcc`

## What ran

| | |
|---|---|
| run date | 2026-09-17T00:18:03.602650+00:00 |
| engine commit | `3df1a4d232bbd9410d8e8e205f198c29ac83255e` |
| engine branch | `bench/locomo-conventions-reader-width` |
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
- `reference/`: the same run graded under the reference harness conventions: its manifest, with the conventions, prompt hashes and differences, and one row per non-adversarial question.
