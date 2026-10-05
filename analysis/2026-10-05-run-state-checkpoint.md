# Run state, and how to resume it by hand

Written 2026-10-05 under a cost freeze. Nothing in this repository or on this
machine will resume any of it on its own: every step below has to be started
deliberately. Run B is deliberately not started.

## Auto-resume mechanisms: what existed and what is left

| mechanism | state |
|---|---|
| `runs/wait_and_launch.py`, the login/cap-probing launcher that started work on its own | **deleted** |
| background launcher, driver, supervisor and monitor processes | **none running**; a process scan for `wait_and_launch`, `settle_driver`, `stage1_seen`, `bench.supervise`, `bench.core.run`, `reference_pass`, `extraction_coverage`, `completeness_recall` and `bench.replay` returns nothing |
| Windows scheduled tasks | **none of ours**; 355 tasks scanned, the only text match is AMD's own `\StartCNBM` running `cncmd.exe benchmark`, which ships with the graphics driver |
| startup folders (per-user and all-users) | **empty** |
| registry `Run` and `RunOnce` keys (HKCU and HKLM) | **nothing of ours**; the entries are Discord, Riot, Logitech, AMD, Postman, Docker Desktop, Adobe, Security Health, SteelSeries and Corsair |
| stale `supervisor.lock` files | **removed** (four) |
| Docker containers `engraphy-settle-pg`, `engraphy-levers-pg`, `engraphy-dates-pg` | Docker Desktop is not running and no container has a restart policy set. Docker Desktop itself is in HKCU `Run`, so it starts with Windows and may start containers with it. A database cannot run a measurement or spend any model allowance; it only has to be up for the replay steps below. |
| `runs/settle_driver.py` | kept, and **inert**: it only runs when invoked. Note that invoking it with two run ids rolls straight from run A into run B. Do not pass `locomo-settle-b`. |

## What is finished

| | |
|---|---|
| Seen-split extraction A/B (stage 1) | complete, committed at `results/locomo/locomo-extract-ab-20261002` |
| Run A, strict, held-out seven conversations | complete: 2,972 answers, 2,960 + 12 verdicts, all graded. 74.8% non-adversarial for the combined engine, 72.11% for the shipped-prompt arm. Written up in `analysis/2026-10-03-held-out-run-a-strict.md` |
| Run A paired arm comparison | complete, `results/locomo/locomo-settle-a/arm-compare.json` |

Engine `aa7daa2b9c5f190ee3f10de5b9bf4cbaee44e5a6`, branch `bench/settle-20260930`.
The strict path last changed at `af6c96e`; later commits touch the offline and
reporting tools only.

## What remains, in order, with the exact command

All of it is reader-only against run A's existing store. No ingest is needed and
none should be run: the store is the measurement.

### 1. Run A's matched-convention pass

36 of 1,151 answers exist, on the combined-engine arm, so this resumes. It reads
saved envelopes from files and needs **no database**.

    cd engraphy-bench-settle
    python -m bench.reference_pass --run-dir runs/locomo-settle-a \
        --arm llm_wide-conversational/search_only/always_distinct/k25 \
        --judge-passes 1 --concurrency 3 --judge-concurrency 4

Idempotent: rerun it and it continues from `reference/answers.jsonl` and
`reference/verdicts.jsonl`. Roughly 1,115 reference answers and 1,151 single-pass
judge calls remain.

### 2. The k=20 and roster-on replays

Both are replays against run A's store, so they cost reader calls and no ingest.
They need the database up:

    docker start engraphy-settle-pg

Then, from `engraphy-bench-roster` (merged up to the measured engine):

    export ENGRAPHY_TEST_DATABASE_URL="postgres://postgres:engraphy@127.0.0.1:5442/engraphy_bench?sslmode=disable"
    python -m bench.completeness_recall --run-dir ../engraphy-bench-settle/runs/locomo-settle-a \
        --arm llm_wide-conversational/search_only/always_distinct/k25 --out <envelope dir>
    python -m bench.replay --envelopes <envelope dir>/<arm>.jsonl ...

### 3. The consolidated run A report

Strict and matched-convention, per category, against Mem0, Mem0-graph and Zep
under the corrected alignment, with the lever's held-out effect and the caveats.
One run means no spread, so the wording is level-with, not ahead, wherever a
single run cannot support ahead.

### 4. Not scheduled, and not to be started without a decision

- **Run B.** It is the only thing that would give the run-to-run spread, and it
  needs a fresh ingest of seven conversations. Frozen.
- A diagnostic fix held back so as not to edit the engine mid-measurement: a
  failed judge call leaves no record of which row failed or why, which is why 12
  rows of run A needed a second pass with nothing to explain them.
- Five memory nodes staged in
  `analysis/PENDING-MEMORY-2026-10-01-settling-measurement.md`; the Engraphy
  server has been refusing connections on 127.0.0.1:8000 since 2026-09-30.
