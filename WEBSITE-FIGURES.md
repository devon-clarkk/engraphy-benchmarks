# LoCoMo figures for engraphy.tech and comparison-site submissions

The authoritative figures for any public surface. Quote them verbatim, with the
caveat line that sits under each. Every number traces to
`results/locomo/locomo-settle-a/` and recomputes with:

    python scripts/consolidate.py results/locomo/locomo-settle-a

Full methodology, including the category alignment and what a single run does and
does not support: `analysis/2026-10-06-locomo-run-a-consolidated-report.md`.

**Source run.** `locomo-settle-a`, 2026-10-03. Engine `aa7daa2`
(`devon-clarkk/engraphy`, branch `bench/settle-20260930`). Reader Claude Opus 4.8,
judge Claude Sonnet 5. 1,486 questions over the seven LoCoMo conversations no
tuning touched: conv-41, conv-42, conv-43, conv-44, conv-47, conv-48, conv-50.
1,151 of them non-adversarial, 335 adversarial.

---

## Headline, like-for-like

**91.0% on LoCoMo, excluding adversarial questions, measured under the same
conventions the published figures use.** 1,047 of 1,151. 95% interval 89.2 to
92.5.

> Caveat line: one run, on the seven LoCoMo conversations held out from tuning,
> graded under the conventions vendored from `mem0ai/memory-benchmarks` at
> `4b61c5d`.

## Engraphy's own stricter number

**74.8% on the same questions under Engraphy's strict convention**, where the
reader may say it does not know and the judge requires every item of the gold
answer. 861 of 1,151. 95% interval 72 to 77.

> Caveat line: Engraphy's strict convention is harder than the one the published
> figures use, so this is the conservative figure, not a like-for-like one.

## Per category, like-for-like

| category | Engraphy | Mem0 | Mem0-graph | Zep |
|---|---|---|---|---|
| excluding adversarial | **91.0%** | 66.9% | 68.4% | 75.1% |
| single-hop | **92.7%** | 72.9% | 75.7% | 76.6% |
| multi-hop | **93.6%** | 67.1% | 65.7% | 61.7% |
| temporal reasoning | **90.7%** | 55.5% | 58.1% | 49.3% |
| open-domain | **68.6%** | 51.2% | 47.2% | 41.4% |

> Caveat line: Engraphy measured under the published conventions on one run over
> seven conversations; comparators as published by Mem0 (arXiv:2504.19413,
> Table 2), with the Zep overall taken from Zep's own higher self-reported figure
> of 75.14% +/- 0.17. Category columns realigned, see the report.

## Per category, Engraphy's strict convention

| category | Engraphy | Mem0 | Mem0-graph | Zep |
|---|---|---|---|---|
| excluding adversarial | 74.8% | 66.9% | 68.4% | 75.1% |
| single-hop | 83.0% | 72.9% | 75.7% | 76.6% |
| multi-hop | 55.9% | 67.1% | 65.7% | 61.7% |
| temporal reasoning | **74.7%** | 55.5% | 58.1% | 49.3% |
| open-domain | 52.9% | 51.2% | 47.2% | 41.4% |
| adversarial, declines correctly | **89.9%** | not reported | not reported | not reported |

> Caveat line: these put Engraphy's harder convention against figures produced
> under the permissive one, so they understate Engraphy relative to the
> like-for-like table. Under this convention multi-hop is behind all three.

## Open-domain sample size

Open-domain is 70 questions on this split, so quote it with its size or its
interval (like-for-like 68.6%, interval 57 to 78).

---

## Approved wording

Use these as written. Each is supported by one run.

- "91.0% on LoCoMo, measured under the same conventions as the published Mem0,
  Mem0-graph and Zep figures."
- "Under matched conventions, Engraphy scored the highest figure in every LoCoMo
  category, including multi-hop."
- "Engraphy leads every LoCoMo category under the published evaluation
  conventions, by 16 to 33 points."
- "74.8% under Engraphy's own stricter convention, where the system is allowed to
  say it does not know."
- "89.9% on LoCoMo's adversarial questions, which the system is expected to
  decline. The published comparisons do not report this category."
- "Measured on the seven LoCoMo conversations held out from all tuning."

Why "leads every category" is safe on one run: the smallest margin is +15.8
points, against Zep's own self-reported figure, and the lower bound of Engraphy's
95% interval (89.2%) sits 14 points above the highest competitor figure including
its stated error. No plausible run-to-run variation closes a gap that size.

## Wording that needs run B first

Do not use these until a second run gives the run-to-run spread.

- Anything averaged or stabilised: "averages 91%", "91.0% +/- x", "consistently
  above 90%", "typically", "repeatable", "stable across runs", "robust". One run
  has no spread.
- "Best-in-class memory" or "the best memory system on LoCoMo" as a standing
  property. On one run, say what was measured instead: "scored the highest figure
  in every LoCoMo category under the published conventions". The measured claim is
  defensible; the standing claim is not yet.
- Any lead drawn from the strict table's overall figure. 74.8% against Zep's
  self-reported 75.14% is **level**, a 0.34-point gap, and no wording should make
  it a lead.
- "Engraphy improves accuracy by 2.7 points" stated as a settled effect of the
  wider extraction prompt. It is significant against chance (p 0.016) but has not
  been checked against run-to-run variation.

## Caveats to show wherever a comparison appears

- **Sample:** 7 of LoCoMo's 10 conversations, the ones held out from tuning. The
  published figures cover all 10.
- **Runs:** one run. Mem0's published figure is the mean of 10.
- **Models:** Claude Opus 4.8 reader, Claude Sonnet 5 judge. The published figures
  use a GPT-4o-mini reader.
- **Context budget:** Engraphy competes with at most 25 memories in context, where
  the matched convention permits 200.
- **Category alignment:** the Mem0 paper's per-category column headers do not name
  the LoCoMo categories they hold. These tables use the one assignment of 24 that
  reproduces the paper's own published overall for all five systems it reports, to
  within 0.01. Method and sources in the report.
- **Zep:** Mem0 published 65.99% for Zep; Zep self-reports 75.14% +/- 0.17. The
  higher figure is used throughout.
- **Mem0's own 92.5%** (mem0.ai/research) is not used as a comparator: it states
  no retrieval budget, answerer or judge model, judge prompt or run count.
- **Matched-convention figure is raw:** the confabulation controls that bounded
  the earlier seen-split figure have not been rerun for this run.
- **Licence:** LoCoMo is CC BY-NC 4.0. Whether to use these figures in commercial
  marketing is an open decision, see `PUBLISH.md`. The dataset itself is not
  redistributed.

## Superseded

The earlier measurement at width 20 over the three tuning conversations is kept
at `results/locomo/locomo-definitive-20260917/`, and the seen-split extraction
comparison at `results/locomo/locomo-extract-ab-20261002/`. Those directories
describe their own scope. Public copy quotes this file.
