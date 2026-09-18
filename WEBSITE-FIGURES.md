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
| single-hop | 69.0% | 67.1% | 65.7% | 61.7% |
| multi-hop | 53.8% | 51.2% | 47.2% | 41.4% |
| temporal reasoning | **72.9%** | 55.5% | 58.1% | 49.3% |
| open-domain | 69.2% | 72.9% | 75.7% | 76.6% |
| adversarial (declines correctly) | **89.2%** | not reported | not reported | not reported |

Comparator figures: Chhikara et al., arXiv:2504.19413, Table 1, LLM-as-a-Judge.

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

## Wording rules

- Level with the leaders, never ahead of them on a single scalar. "Level with Mem0 on
  LoCoMo, and ahead on temporal reasoning" is accurate. "Beats Mem0" is not supported.
- Quote the strict figure first. Label the 86.1% every time as measured under the
  reference harness conventions.
- The adversarial figure is Engraphy's own; the published comparisons exclude that
  category.

## Caveats, shown wherever a comparison is

- **Sample:** 3 of LoCoMo's 10 conversations. The published figures cover all 10.
- **Runs:** one run. The published figures are the mean of 10.
- **Models:** Claude Opus 4.8 reader and Claude Sonnet 5 judge. The published figures use
  a GPT-4o-mini reader.
- **Category names:** the Mem0 paper does not state which LoCoMo category number each of
  its category names covers.
- **Zep:** the Zep column is Mem0's measurement of Zep, which Zep disputes.
- **Licence:** LoCoMo is CC BY-NC 4.0. Using these figures in commercial marketing is an
  open decision; see PUBLISH.md.
