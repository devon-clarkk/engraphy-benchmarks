# Retrieval completeness: measured recovery on the single-hop and multi-hop failures

Date: 2026-09-25. Decision rules fixed before measurement in
`analysis/2026-09-19-retrieval-completeness-preregistration.md` (commit `fbbf1a5`).
Prototype: `devon-clarkk/engraphy` branch `feat/entity-complete-retrieval`.
Store and questions: run `locomo-definitive-20260917` (318 memories, conv-26,
conv-30, conv-49; 389 non-adversarial and 111 adversarial questions).

## 1. Result

Both additions do what they were designed to do in retrieval, and **neither
passes its pre-registered rule to ship.**

- **The entity roster is safe but unproven.** It gains 5 non-adversarial
  questions (p = 0.46) and costs no adversarial declines. Its target category,
  multi-hop, gains 6 (+10 / -4, p = 0.18). Directionally right, not resolvable on
  80 multi-hop questions.
- **The source-turn backstop is large but breaks the adversarial guard.** Added
  on top of the roster it gains 21 non-adversarial questions (p = 0.0025) and
  loses 8 adversarial declines (p = 0.02), a significant regression.

The rules are applied as written rather than reinterpreted now that the numbers
are known. What to do with each is in section 8.

## 2. Arms

| Arm | Envelope |
|---|---|
| C0 | hybrid search k=25, the staged run's configuration, and the control |
| A1 | C0 plus the entity roster |
| A2 | C0 plus the roster plus the source-turn backstop |

Every arm re-reads all 500 questions from saved envelopes under the definitive
reader (`claude-opus-4-8`, stance `grounded`, contract `verify`, skill
`sha256:c3b00290...`), graded by the unchanged strict judge, one pass; adversarial
questions by the abstention rule. C0 is a fresh read, so each comparison differs
only in the envelope.

## 3. Retrieval coverage, with no LLM

`bench.completeness_recall` rebuilt retrieval for every question against the kept
store; its k=20 arm reproduced 498 of the run's 500 saved envelopes id for id.
Share of non-adversarial questions with **all** their evidence in context:

| Arm | All evidence | Context chars |
|---|---|---|
| k=20 (the definitive run) | 66.2% | 12.2k |
| k=25 (control) | 66.9% | 15.2k |
| k=25 + roster | 71.1% | 21.6k |
| k=25 + turns | 80.1% | 16.9k |
| k=25 + both | 84.2% | 23.3k |
| flat 50, width control | 67.4% | 17.9k |
| entity-filtered 50, full bodies | 70.0% | 30.0k |

Width alone buys almost nothing: fifty results reach 67.4% against 66.9% at
twenty-five. Both legs of hybrid search cap at 30 candidates before fusion, so a
memory whose wording does not resemble the query cannot be reached by widening.
That is the control that makes the rest meaningful.

## 4. Reader accuracy, paired per question

| | C0 | A1 (roster) | A2 (roster + turns) |
|---|---|---|---|
| Non-adversarial | 68.4% (266/389) | 69.7% (271/389) | **75.1% (292/389)** |
| single-hop | 129 | 130 | 146 |
| multi-hop | 45 | **51** | 50 |
| temporal | 74 | 72 | 77 |
| open-domain | 18 | 18 | 19 |
| Adversarial | 99/111 | **101/111** | 93/111 |

| Comparison | Non-adversarial | Adversarial |
|---|---|---|
| definitive k=20 to C0 (churn floor) | +14 / -8, net +6, p = 0.29 | +2 / -2, net 0 |
| C0 to A1 | +17 / -12, net +5, p = 0.46 | +3 / -1, net +2 |
| A1 to A2 (the turns' own effect) | +33 / -12, net +21, p = 0.0025 | +1 / -9, net **-8**, p = 0.02 |
| C0 to A2 | +36 / -10, net +26, p = 0.0002 | +1 / -7, net -6, p = 0.07 |

Re-reading the same questions changes about 5% of verdicts in both directions, so
the +6 churn floor is the bar any gain must clear. A1's +5 does not clear it.

## 5. Recovery on the failure classes this work owns

Questions the definitive run got wrong that are correct in the arm.

| Class | n | C0 | A1 | A2 |
|---|---|---|---|---|
| single-hop, evidence never extracted | 34 | 1 | 2 | **18** |
| single-hop, evidence stored but not retrieved | 4 | 0 | 0 | 1 |
| multi-hop, evidence stored but not retrieved | 12 | 1 | 3 | 3 |
| multi-hop, evidence never extracted | 12 | 2 | 2 | 3 |
| multi-hop, evidence already complete in context | 13 | 2 | **7** | 4 |
| single-hop, evidence already complete in context | 20 | 2 | 1 | 2 |

Each mechanism moves its own class. Extraction gaps, where no stored memory
quotes the evidence, move only with the source turns: no read-path change can
retrieve a fact that was never written. Retrieval gaps move with the roster. The
roster also helps multi-hop questions whose evidence was already complete,
which fits its shape: a complete titled list of what is known about a person
makes a set question answerable where scattered full bodies did not.

## 6. What the source-turn backstop actually does to the reader

Declines, out of 389 non-adversarial and 111 adversarial:

| Arm | non-adversarial declines | adversarial declines (correct) |
|---|---|---|
| C0 | 43 | 99 |
| A1 | 43 | 101 |
| A2 | 24 | 93 |

The roster leaves decline behaviour untouched. The backstop moves the reader
toward answering everywhere: 19 fewer declines on answerable questions, of which
most become correct answers, and 6 fewer on traps, all of which become wrong.
The gain and the cost are the same shift measured on two populations.

## 7. Why adversarial inflated

The seven adversarial questions A2 lost are all misattribution traps: the
question asks what Caroline said when Melanie said it, what Jon wanted for a
store that is Gina's, what Sam limited when it was Evan. Declining is correct.

Mapping each reader CHECK line onto the envelope numbering, six of the seven cite
a **source turn**; the seventh cites a memory inside the baseline k=25 results
and is ordinary churn. One CHECK line states the misattribution outright and
answers anyway ("the ginger snap limit in [1]/[95] is Evan's, not Sam's").

A raw turn carries words without the attribution a typed memory's title supplies,
so a trap question finds matching words spoken by the other person. Whether the
reader should answer on that evidence is the reader workstream's lever; that this
retrieval addition raises the temptation is this workstream's finding.

## 8. Recommendation

**Entity roster: keep, do not ship on this evidence, re-measure at scale.** It is
adversarially safe, costs about 6k characters of context, and its effect sits
inside this sample's noise. The claim it would support is category-specific, and
the staged ten-conversation run carries 282 multi-hop questions against 80 here.
Specify it as an engine search option, default off, and measure it there as a
second arm over the same ingest.

**Source-turn backstop: do not ship as measured.** The gain is real and large,
and so is the regression. Two things must happen before it could be reconsidered,
in this order: the product decision on storing transcripts at all
(`design/01-core-data-model.md` lists that as a non-goal), and then an attribution
fix so a turn carries its speaker as a first-class field the reader is required
to check, rather than as text. Rerunning it without that fix would reproduce the
same trade.

**Neither belongs in the staged run as harness-only code.** A harness-only
retrieval path is a configuration no deployment can reproduce.

## 9. Provenance

- Prototype and instrument: `feat/entity-complete-retrieval`, commits `bdc6c17`,
  `76ee47d`.
- Arms: `runs/locomo-definitive-20260917/replay/{c0-k25,a1-k25-roster,a2-k25-both}`.
- Coverage: `runs/locomo-definitive-20260917/completeness/summary.json`.
- Engine specification: `design/analysis/retrieval-completeness.md` on that branch.
