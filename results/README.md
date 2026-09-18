# Results

One directory per run, under the benchmark's name. Every file in a run directory
is produced from the run itself; nothing is typed by hand.

| file | what it holds |
|---|---|
| `PROVENANCE.md` | the headline and per-category figures, what ran and where, rendered from the files beside it |
| `manifest.json` | the engine harness's manifest: engine commit, dataset digest, models requested and served, prompt and pack hashes, thresholds, aggregates |
| `results.jsonl` | one row per question, keyed by `question_id`: category, verdict, best-of-3 tally and the system's answer |
| `ingest.jsonl` | per-conversation write statistics: memories extracted, memories stored, refusals by class |
| `provenance.json` | host, runtime and package versions, Postgres and pgvector versions (runs produced by `reproduce.py`) |
| `config.json` | the `config/locomo.json` the run was produced with (runs produced by `reproduce.py`) |

No file carries LoCoMo question text, gold answers or conversation text. Restore
them from your own copy of the dataset with `scripts/rejoin.py`.

## LoCoMo

Arm `llm-conversational/search_only/always_distinct`, conversations `conv-26`,
`conv-30` and `conv-49`. Brackets are 95% Wilson intervals.

| run | engine | excluding adversarial | all five categories | per-pass judge instability | write-yield |
|---|---|---|---|---|---|
| [`locomo-definitive-20260917`](locomo/locomo-definitive-20260917/PROVENANCE.md) | `3df1a4d` (PR #23, levers 2 to 4) | 66.8% [62 to 71] (260/389) | 71.8% [68 to 76] (359/500) | 2.5% (1/40) | 95.2% (318/334) |
| [`fullrun-conv-20260916`](locomo/fullrun-conv-20260916/PROVENANCE.md) | public `67dd41a` | 60.2% [55 to 65] (234/389) | 63.2% [59 to 67] (316/500) | 0.0% (0/40) | 85.7% (269/314) |
| [`fullrun-conv-20260809`](locomo/fullrun-conv-20260809/PROVENANCE.md) | development `631e7be` | 67.1% [62 to 72] (261/389) | 71.6% [67 to 75] (358/500) | not measured | 99.4% (346/348) |

Write-yield is the share of extracted memories the engine stored. Per-pass judge
instability is the share of a sample, each item graded twice with a single judge
pass, on which the two passes disagreed; the best-of-3 majority verdict that
scores a run changes less often than a single pass. [METHODOLOGY.md](../METHODOLOGY.md) explains which engine produced which
figure.
