# LoCoMo figures for engraphy.tech

The authoritative figures for any public surface. Every number traces to
`results/locomo/locomo-definitive-20260917/` and recomputes with
`python scripts/verify_definitive.py`. Use them as written, with their caveats.

Source run: `locomo-definitive-20260917`, 2026-09-17. Engine `3df1a4d`
(`devon-clarkk/engraphy`, PR #23 plus the reader check and search width 20).
Reader Claude Opus 4.8, judge Claude Sonnet 5. 500 questions over LoCoMo
conversations conv-26, conv-30 and conv-49.

## Headline

**66.8% on LoCoMo, excluding adversarial questions, under Engraphy's strict
conventions**: the reader may say it does not know, and the judge requires every item
of the gold answer. 95% interval 62 to 71 (260 of 389).

## Per category, strict conventions

| category | Engraphy | Mem0 | Mem0g | Zep |
|---|---|---|---|---|
| excluding adversarial | **66.8%** | 66.9% | 68.4% | 66.0% |
| single-hop | 69.0% | 72.9% | 75.7% | 76.6% |
| multi-hop | 53.8% | 67.1% | 65.7% | 61.7% |
| temporal reasoning | **72.9%** | 55.5% | 58.1% | 49.3% |
| open-domain | **69.2%** | 51.2% | 47.2% | 41.4% |
| adversarial (declines correctly) | **89.2%** | not reported | not reported | not reported |

Comparator figures: Chhikara et al., arXiv:2504.19413, Table 1 (LLM-as-a-Judge), aligned to LoCoMo's
category numbers. Table 1's column headers do not name the categories they hold. The paper's
overall score (Table 2) is the question-weighted mean of the four categories, whose sizes differ
(282, 321, 96 and 841 questions), so each of the 24 ways to assign the four columns to the four
categories predicts a different overall. One assignment reproduces the published overall for all
five systems reported in both tables, to within 0.01 points; the next best misses by up to 1.06,
and reading the headers as the dataset names them misses by 1.8 to 9.7. Under it, the paper's
"Single-Hop" column holds LoCoMo multi-hop (category 1), "Multi-Hop" holds open-domain
(category 3) and "Open-Domain" holds single-hop (category 4); "Temporal" is category 2 either
way. Method and sources: `analysis/2026-09-19-locomo-open-domain-findings.md`, section 3 and
its source list, recorded in proj-engraphy as the Fable analysis node `d7c05bc3`.

## Under the reference harness conventions

**86.1% excluding adversarial, measured under the reference harness conventions for
comparability (range 76% to 89%).**

The same run, graded with the answer prompt and judge of `mem0ai/memory-benchmarks`. The
range runs from answers Engraphy's strict judge also accepts (75.6%) to everything the
reference judge accepts (88.9%). 86.1% removes the credits the reference rules give where
the evidence was absent from retrieved memory. Quote the range with the figure.

## The claim that survives every caveat

**Temporal reasoning: 72.9% under the strict judge, against the best published 58.1%
(Mem0g).**

Open-domain also leads, 69.2% against the best published 51.2% (Mem0), on 26
questions (interval 50 to 84): state it with its sample size. Single-hop and multi-hop
trail the published figures and are shown as they are.

## Wording rules

- Level with the leaders, never ahead of them on a single scalar. "Level with Mem0 on
  LoCoMo, ahead on temporal reasoning and open-domain, behind on single-hop and
  multi-hop" is accurate. "Beats Mem0" is not supported.
- Quote the strict figure first. Label the 86.1% every time as measured under the
  reference harness conventions.
- The adversarial figure is Engraphy's own; the published comparisons exclude that
  category.

## Caveats, shown wherever a comparison is

- **Sample:** 3 of LoCoMo's 10 conversations. The published figures cover all 10.
- **Runs:** one run. The published figures are the mean of 10.
- **Models:** Claude Opus 4.8 reader and Claude Sonnet 5 judge. The published figures use
  a GPT-4o-mini reader.
- **Category alignment:** the Mem0 paper's Table 1 headers do not name the LoCoMo
  categories they hold. The table above uses the one assignment that reproduces the
  paper's published overall for all five systems; see the note under the table.
- **Zep:** the Zep column is Mem0's measurement of Zep, which Zep disputes.
- **Licence:** LoCoMo is CC BY-NC 4.0. Using these figures in commercial marketing is an
  open decision; see PUBLISH.md.
