# Provenance: `locomo-settle-a`

Run A on the held-out seven conversations: the combined engine (width 25, wider extraction prompt) and the shipped extraction prompt as a second arm on one ingest, strict convention, plus the matched-convention pass over the combined engine's saved envelopes.

## Result

Arm `llm-conversational/search_only/always_distinct/k25`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **72.1% [69 to 75] (830/1151)** |
| overall, all five categories | 75.9% [74 to 78] (1128/1486) |
| adversarial | 89.0% [85 to 92] (298/335) |
| multi-hop | 55.5% [49 to 62] (112/202) |
| open-domain-knowledge | 51.4% [40 to 63] (36/70) |
| single-hop | 78.9% [76 to 82] (516/654) |
| temporal-reasoning | 73.8% [68 to 79] (166/225) |

Arm `llm_wide-conversational/search_only/always_distinct/k25`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **74.8% [72 to 77] (861/1151)** |
| overall, all five categories | 78.2% [76 to 80] (1162/1486) |
| adversarial | 89.8% [86 to 93] (301/335) |
| multi-hop | 55.9% [49 to 63] (113/202) |
| open-domain-knowledge | 52.9% [41 to 64] (37/70) |
| single-hop | 83.0% [80 to 86] (543/654) |
| temporal-reasoning | 74.7% [69 to 80] (168/225) |

Per-pass judge instability, two single judge passes compared on a sample: 5.0% (2 of 40 items graded twice). The best-of-3 majority verdict changes less often than a single pass.
Write-yield at ingest: 99.5% (2831 of 2846 extracted memories stored).

## Under the reference harness conventions

Measured measured under the reference harness conventions, for comparability, over the same run: every non-adversarial question read again from the envelope the run saved, under the answer prompt and judge of [https://github.com/mem0ai/memory-benchmarks](https://github.com/mem0ai/memory-benchmarks) at `4b61c5d31b9c` (Apache-2.0). The strict figure above is Engraphy's primary figure.

Arm `llm_wide-conversational/search_only/always_distinct/k25/reference-conventions`, 95% Wilson intervals in brackets.

| | accuracy |
|---|---|
| **excluding adversarial** | **91.0% [89 to 92] (1047/1151)** |
| multi-hop | 93.6% [89 to 96] (189/202) |
| open-domain-knowledge | 68.6% [57 to 78] (48/70) |
| single-hop | 92.7% [90 to 94] (606/654) |
| temporal-reasoning | 90.7% [86 to 94] (204/225) |

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
| run date | 2026-10-01T23:40:47.342748+00:00 |
| engine commit | `b9a3afc10c42880614ff046b840dee221bd708a9` |
| engine branch | `bench/settle-20260930` |
| engine tree dirty | False |
| dataset | `locomo10.json` `sha256:79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`, 1986 questions in the file |
| conversations | `conv-41`, `conv-42`, `conv-43`, `conv-44`, `conv-47`, `conv-48`, `conv-50` |
| extractor | `claude-opus-4-8` via claude-cli |
| reader | `claude-opus-4-8` via claude-cli |
| judge | `claude-sonnet-5` via claude-cli, provider `claude` |
| reader stance | `grounded` |
| embedding model | `nomic-ai/nomic-embed-text-v1.5` at `e9b6763023c676ca8431644204f50c2b100d9aab` |
| band thresholds | {"t_high": 0.95, "t_low": 0.8, "resonance.floor": 0.75} |
| prompt hashes | `extract.md` sha256:b7fdf557f7f60a9c, `extract-wide.md` sha256:2f3fa4c9e6c1a457, `judge.md` sha256:947bebcd5375e93e, `adjudicate.md` sha256:740151c30787a630 |
| models that served | judge: `claude-opus-5`, `claude-sonnet-5`; reader: `claude-opus-4-8` (the CLI reports every model that ran in a call, including one it runs for its own internal work, so a role can list two) |

## Where it ran

Host and runtime were not captured for this run.

## Files

- `manifest.json`: the harness manifest, with extracted-memory text removed from its ingest samples.
- `results.jsonl`: one row per question, keyed by `question_id`, with the verdict, the best-of-3 tally and the system's answer. No question text, gold answers or conversation text; restore them from your own copy with `scripts/rejoin.py`.
- `ingest.jsonl`: per-conversation write statistics, including every class of write refusal and the engine's message for it.
- `reference/`: the same run graded under the reference harness conventions: its manifest, with the conventions, prompt hashes and differences, and one row per non-adversarial question.
