# Engraphy benchmarks

Reproducible benchmarks for [Engraphy](https://github.com/devon-clarkk/engraphy),
a memory engine for AI agents. One command runs the engine's LoCoMo harness at a
pinned engine commit, and every committed result carries the provenance needed to
check it.

## LoCoMo and its licence

LoCoMo is **not** in this repository and is never committed to it. Its authors
(Maharana et al., ACL 2024) publish it under
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), which permits
non-commercial use with attribution. `scripts/fetch_locomo.py` downloads
`locomo10.json` and its licence file from
[snap-research/locomo](https://github.com/snap-research/locomo) at a pinned
upstream commit, and verifies the sha256 recorded in `config/locomo.json`. Your
use of the data is governed by its licence, not by this repository's. The
citation is in [NOTICE](NOTICE).

Committed results carry question ids, categories, verdicts and the system's own
answers. They carry no question text, gold answers or conversation text.
`scripts/rejoin.py` restores those locally from your own copy for auditing, and
a guard refuses to publish any result file that quotes a dataset question.

## Results

Arm `llm-conversational/search_only/always_distinct` over LoCoMo conversations
`conv-26`, `conv-30` and `conv-49`: 500 questions, 389 of them non-adversarial.
The headline figure excludes the adversarial category, the convention published
memory-system figures use, and the figure across all five categories is reported
beside it. Brackets are 95% Wilson intervals.

| run | engine | excluding adversarial | all five categories | provenance |
|---|---|---|---|---|
| **2026-09-17** | `devon-clarkk/engraphy` at `3df1a4d` (PR #23, reader check, search width 20) | **66.8% [62 to 71] (260/389)** | 71.8% [68 to 76] (359/500) | [PROVENANCE.md](results/locomo/locomo-definitive-20260917/PROVENANCE.md) |
| 2026-09-16 | public `devon-clarkk/engraphy` at `67dd41a` | 60.2% [55 to 65] (234/389) | 63.2% [59 to 67] (316/500) | [PROVENANCE.md](results/locomo/fullrun-conv-20260916/PROVENANCE.md) |
| 2026-08-09 | Engraphy development branch at `631e7be` | 67.1% [62 to 72] (261/389) | 71.6% [67 to 75] (358/500) | [PROVENANCE.md](results/locomo/fullrun-conv-20260809/PROVENANCE.md) |

The current measurement is two independent runs, each re-ingesting from scratch,
over the seven conversations held out from all tuning, `conv-41`, `conv-42`,
`conv-43`, `conv-44`, `conv-47`, `conv-48` and `conv-50`: 1,486 questions per
run, 1,151 of them non-adversarial. Reported as the mean of the two runs with the
range across them.

| run | engine | strict, excluding adversarial | matched convention | provenance |
|---|---|---|---|---|
| **mean of both** | `EngraphyLabs/engraphy` at `aa7daa2` (search width 25, wider extraction prompt) | **75.4% (range 74.8 to 76.0)** | **91.4% (range 91.0 to 91.8)** | |
| 2026-10-03, run A | same | 74.8% [72 to 77] (861/1,151) | 91.0% [89 to 92] (1,047/1,151) | [PROVENANCE.md](results/locomo/locomo-settle-a/PROVENANCE.md) |
| 2026-10-09, run B | same | 76.0% (875/1,151) | 91.8% (1,057/1,151) | [PROVENANCE.md](results/locomo/locomo-settle-b/PROVENANCE.md) |

`python scripts/consolidate.py results/locomo/locomo-settle-a results/locomo/locomo-settle-b`
recomputes both figures, the spread between the runs, and the per-category
standing against the published Mem0, Mem0-graph and Zep results. The
[consolidated report](analysis/2026-10-09-locomo-two-run-consolidated-report.md)
states the methodology, the category alignment and every caveat, and
[WEBSITE-FIGURES.md](WEBSITE-FIGURES.md) carries the publishable set with the
wording each figure supports.

The 2026-09-17 run is also graded under the reference harness conventions, for
comparability with published figures: 86.1% excluding adversarial, range 75.6% to
88.9%, with its validity controls in `reference/`. `python scripts/verify_definitive.py`
recomputes both figures from the committed files, and
[WEBSITE-FIGURES.md](WEBSITE-FIGURES.md) states the figures for public use with their
caveats.

Each PROVENANCE.md gives the per-category figures, the models that served each
role, the exact engine commit, dataset digest and thresholds, and the host and
runtime. [METHODOLOGY.md](METHODOLOGY.md) explains what LoCoMo measures, which
engine produced which figure, and what these figures are and are not comparable
to.

## Reproduce

Requirements: git, Docker, Python 3.12 or later, and the
[Claude Code](https://github.com/anthropics/claude-code) CLI, signed in. At
the pinned engine commit the extractor, reader and judge are reached through the
CLI, so a run draws on the signed-in account's usage. It pauses at a usage limit
and resumes on its own.

```bash
git clone https://github.com/devon-clarkk/engraphy-benchmarks
cd engraphy-benchmarks
python reproduce.py --smoke   # full setup, then one conversation ingested, no model called
python reproduce.py           # the full run
```

`reproduce.py`:

1. clones the engine at the commit pinned in `config/locomo.json` and refuses any
   other commit or a modified tree;
2. builds a virtualenv with the engine installed from that checkout;
3. starts a pgvector Postgres in Docker on `127.0.0.1:5439`, applies every engine
   migration and provisions the app role with the engine's own script;
4. downloads LoCoMo from its authors and verifies its sha256;
5. runs the engine's harness with exactly the arm, conversations, models, judge
   and phases in the config;
6. grades the same run under the reference harness conventions, the second
   figure, reported beside the strict one for comparability (`--strict-only` skips it);
7. records the host, runtime and database versions;
8. writes the committable subset of both to `results/locomo/<run-id>/` and prints
   both headline tables.

Run the same command again to resume an interrupted run. `--prepare-only` stops
after setup and prints the exact harness command, and `--dry-run` prints the plan
without running anything. The 2026-09-16 run took 80 minutes of active running time on the hardware its provenance records, in 2 cycles either side of a pause at a Claude usage limit.

The extractor, reader and judge are sampled models, so a reproduction measures
the same pipeline rather than replaying the same verdicts. Read a difference
against the intervals and the judge instability each run records.

## Score another memory system

`grade.py` grades any system's answers with the judge, prompt, best-of-3 majority
and adversarial rule that scored Engraphy, imported from the pinned engine rather
than copied. The integration point is a JSONL file of
`{"question_id": ..., "answer": ...}`:

```bash
python grade.py answers.jsonl --system my-memory-system
```

[ADAPTERS.md](ADAPTERS.md) has the contract and what a submission should state.

## Layout

```
config/locomo.json      the configuration of the published run; reproduce.py reads it by default
config/locomo-next.json the next run, staged and held until its engine commit is pinned
reproduce.py            the one-command path
grade.py                grade another system's answers with the same judge
benchkit/               dataset fetch and verify, engine checkout, database, redaction, provenance
scripts/                fetch, redact, rejoin, convert a run to answers, render provenance,
                        recompute the definitive figures from the committed files
results/locomo/<run>/   committed results: manifest, per-question verdicts, ingest statistics, provenance
METHODOLOGY.md          what is measured, what is pinned, what is comparable
WEBSITE-FIGURES.md      the figures for public use, with their caveats
PUBLISH.md              the publishing checklist
analysis/               the diagnosis, the pre-registered decision rules, the definitive results
ADAPTERS.md             the answers contract for other systems
tests/                  run on every push, against an invented fixture
```

This repository is versioned separately from the engine, so that each result
names the engine commit it measured and a new engine release never changes a
committed result.

## Licence

The code in this repository is Apache-2.0 ([LICENSE](LICENSE)). The Engraphy
engine is fetched separately at run time and is licensed under the Business
Source License 1.1. LoCoMo is CC BY-NC 4.0, downloaded from its authors and
never redistributed here ([NOTICE](NOTICE)).
