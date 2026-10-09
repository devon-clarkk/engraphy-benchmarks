# LoCoMo figures for engraphy.tech and comparison-site submissions

The authoritative figures for any public surface. Quote them verbatim, with the
caveat line that sits under each. Every number traces to
`results/locomo/locomo-settle-a/` and `results/locomo/locomo-settle-b/` and
recomputes with:

    python scripts/consolidate.py results/locomo/locomo-settle-a \
                                  results/locomo/locomo-settle-b

Full methodology, including the category alignment, the conventions and the
caveats: `analysis/2026-10-09-locomo-two-run-consolidated-report.md`.

**Source runs.** `locomo-settle-a` (2026-10-03) and `locomo-settle-b`
(2026-10-09), two independent runs of the same configuration, each re-ingesting
from scratch. Engine `aa7daa2` (`EngraphyLabs/engraphy`, branch
`bench/settle-20260930`), search width 25 with the wider extraction prompt.
Reader Claude Opus 4.8, judge Claude Sonnet 5. Each run covers 1,486 questions
over the seven LoCoMo conversations no tuning touched: conv-41, conv-42, conv-43,
conv-44, conv-47, conv-48, conv-50. 1,151 of them non-adversarial, 335
adversarial.

Figures are the mean of the two runs, with the range across them. Two runs give a
mean and a range, not a standard deviation, so no figure here carries a
plus-or-minus.

---

## Headline, like-for-like

**91.4% on LoCoMo, excluding adversarial questions, measured under the same
conventions the published figures use.** Mean of two runs, range 91.0 to 91.8.
2,104 of 2,302 across both runs, 95% interval 90 to 92.

> Caveat line: mean of two independent runs on the seven LoCoMo conversations
> held out from tuning, graded under the conventions vendored from
> `mem0ai/memory-benchmarks` at `4b61c5d`.

## Engraphy's own stricter number

**75.4% on the same questions under Engraphy's strict convention**, where the
reader may say it does not know and the judge requires every item of the gold
answer. Mean of two runs, range 74.8 to 76.0. 1,736 of 2,302, 95% interval 74 to
77.

> Caveat line: Engraphy's strict convention is harder than the one the published
> figures use, so this is the conservative figure, not a like-for-like one.

## Per category, like-for-like

| category | Engraphy (mean, range) | Mem0 | Mem0-graph | Zep |
|---|---|---|---|---|
| excluding adversarial | **91.4%** (91.0 to 91.8) | 66.9% | 68.4% | 75.1% |
| single-hop | **93.3%** (92.7 to 94.0) | 72.9% | 75.7% | 76.6% |
| multi-hop | **91.8%** (90.1 to 93.6) | 67.1% | 65.7% | 61.7% |
| temporal reasoning | **92.2%** (90.7 to 93.8) | 55.5% | 58.1% | 49.3% |
| open-domain | **69.3%** (68.6 to 70.0), n=140 | 51.2% | 47.2% | 41.4% |

> Caveat line: Engraphy measured under the published conventions, mean of two
> runs over seven conversations; comparators as published by Mem0
> (arXiv:2504.19413, Table 2), with the Zep overall taken from Zep's own higher
> self-reported figure of 75.14%. Category columns realigned, see the report.

## Per category, Engraphy's strict convention

| category | Engraphy (mean, range) | Mem0 | Mem0-graph | Zep |
|---|---|---|---|---|
| excluding adversarial | 75.4% (74.8 to 76.0) | 66.9% | 68.4% | 75.1% |
| single-hop | **83.3%** (83.0 to 83.5) | 72.9% | 75.7% | 76.6% |
| multi-hop | 55.9% (55.9 to 55.9) | 67.1% | 65.7% | 61.7% |
| temporal reasoning | **76.7%** (74.7 to 78.7) | 55.5% | 58.1% | 49.3% |
| open-domain | **54.3%** (52.9 to 55.7), n=140 | 51.2% | 47.2% | 41.4% |
| adversarial, declines correctly | **90.3%** (89.9 to 90.7) | not reported | not reported | not reported |

> Caveat line: these put Engraphy's harder convention against figures produced
> under the permissive one, so they understate Engraphy relative to the
> like-for-like table. Under this convention multi-hop is behind all three.

## Run-to-run spread

| | mean | range across the two runs |
|---|---|---|
| like-for-like | 91.4% | 0.8 points |
| strict | 75.4% | 1.2 points |
| adversarial | 90.3% | 0.9 points |

> Caveat line: two independent runs, each with its own ingest, so the range
> covers extraction variation as well as sampling.

---

## Approved wording

Use these as written.

- "91.4% on LoCoMo, mean of two independent runs, measured under the same
  conventions as the published Mem0, Mem0-graph and Zep figures."
- "Ahead of Mem0, Mem0-graph and Zep on every LoCoMo category under the published
  evaluation conventions, across two independent runs."
- "Ahead on single-hop, temporal reasoning and open-domain even under Engraphy's
  own stricter convention, where the system is allowed to say it does not know."
- "75.4% under Engraphy's own stricter convention, mean of two runs, range 74.8 to
  76.0."
- "90.3% on LoCoMo's adversarial questions, which the system is expected to
  decline. The published comparisons do not report this category."
- "Run-to-run spread is under 1.3 points on both conventions, across two runs
  that each re-ingested the corpus from scratch."
- "The wider extraction prompt adds 2.7 points on held-out data, more than double
  the run-to-run spread."
- "Measured on the seven LoCoMo conversations held out from all tuning."

Why "ahead" is carried by these two runs: under the published conventions every
margin is 16 points or more, and each run's own figure, not only the mean, sits
above every competitor figure including Zep's self-reported one with its stated
error. The run-to-run range is under a point.

## Stays "level", do not upgrade

- **The strict overall figure against Zep's self-reported 75.14%.** The mean is
  75.4% and the run range is 74.8 to 76.0, which straddles it. Say "level with
  Zep's self-reported figure under our stricter convention, ahead of the
  published Mem0 and Mem0-graph figures".

## Off-limits

- **A plus-or-minus on any figure.** Two runs give a mean and a range. Write
  "mean of two runs, range 91.0 to 91.8", never "91.4% +/- 0.4".
- **Strict multi-hop as anything but behind.** 55.9% against 61.7 to 67.1, and
  identically in both runs.
- **"Best memory system" or "best-in-class memory" as a standing property.** Two
  runs, one benchmark, one split, our harness. The measured form is the
  defensible one: "ahead of all three on every LoCoMo category under the
  published conventions".
- **Open-domain without its size.** 140 questions pooled across both runs, 95%
  interval 61 to 76 like-for-like. Quote it with n=140 or with the interval.
- **"Consistently", "stable", "repeatable", "typically".** Two runs support a
  mean and a range, and the range is the honest way to say it.

## Caveats to show wherever a comparison appears

- **Sample:** 7 of LoCoMo's 10 conversations, the ones held out from tuning. The
  published figures cover all 10.
- **Runs:** two independent runs. Mem0's published figure is the mean of 10.
- **Models:** Claude Opus 4.8 reader, Claude Sonnet 5 judge. The published figures
  use a GPT-4o-mini reader.
- **Context budget:** Engraphy competes with at most 25 memories in context, where
  the matched convention permits 200.
- **Category alignment:** the Mem0 paper's per-category column headers do not name
  the LoCoMo categories they hold. These tables use the one assignment of 24 that
  reproduces the paper's own published overall for all five systems it reports, to
  within 0.01. Method and sources in the report.
- **Zep:** Mem0 published 65.99% for Zep; Zep self-reports 75.14%. The higher
  figure is used throughout.
- **Mem0's own 92.5%** (mem0.ai/research) is not used as a comparator: it states
  no retrieval budget, answerer or judge model, judge prompt or run count.
- **The like-for-like figure is raw:** the confabulation controls that bounded the
  earlier three-conversation figure have not been rerun for these runs.
- **Licence:** LoCoMo is CC BY-NC 4.0. Whether to use these figures in commercial
  marketing is an open decision, see `PUBLISH.md`. The dataset itself is not
  redistributed.

## Other measurements in this repository

`results/locomo/locomo-extract-ab-20261002` holds the seen-split extraction
comparison that promoted the wider prompt.
`results/locomo/locomo-definitive-20260917` holds the three-conversation
measurement at width 20, with its own validity controls. Those directories
describe their own scope. Public copy quotes this file.
