# Retrieval completeness: measured recovery on the single-hop and multi-hop failures

Date: 2026-09-25. Decision rules fixed before measurement in
`analysis/2026-09-19-retrieval-completeness-preregistration.md` (commit `fbbf1a5`).
Prototype: `devon-clarkk/engraphy` branch `feat/entity-complete-retrieval`.
Store and questions: run `locomo-definitive-20260917` (318 memories, conv-26,
conv-30, conv-49; 389 non-adversarial and 111 adversarial questions).

## 1. Result in one paragraph

Both additions work as designed on the failure classes they target, and together
they raise non-adversarial accuracy from 68.4% to 75.1%, a paired gain of 26
questions at p = 0.0002 with no category regressing. The combination also costs
six adversarial declines, which breaks the pre-registered guard of at most three,
so **it does not ship as measured**. The adversarial cost is traceable to the
source-turn backstop, not the entity roster: on six of the seven lost
adversarial questions the reader's own CHECK line cites a source turn.

## 2. What was measured

| Arm | Envelope | Status |
|---|---|---|
| C0 | hybrid search k=25, the staged run's configuration | complete |
| A1 | C0 plus the entity roster | grading in progress |
| A2 | C0 plus the roster plus the source-turn backstop | complete |

Every arm re-reads all 500 questions from saved envelopes under the definitive
reader (`claude-opus-4-8`, stance `grounded`, contract `verify`, skill
`sha256:c3b00290...`), graded by the unchanged strict judge, one pass, adversarial
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

Width alone buys almost nothing (67.4% at fifty results against 66.9% at
twenty-five), which is the control that matters: the gain comes from the two
mechanisms, not from retrieving more. Both legs of hybrid search cap at 30
candidates before fusion, so a memory that the query's wording does not resemble
cannot be reached by widening.

## 4. Reader accuracy

Paired per question against C0.

| | C0 | A2 (roster + turns) | change |
|---|---|---|---|
| Non-adversarial | 68.4% (266/389) | **75.1% (292/389)** | +36 / -10, net **+26**, p = 0.0002 |
| single-hop | 129 | 146 | net +17 |
| multi-hop | 45 | 50 | net +5 |
| temporal | 74 | 77 | net +3 |
| open-domain | 18 | 19 | net +1 |
| Adversarial | 99/111 | 93/111 | net **-6**, p = 0.07 |

The reader's own churn is the floor to read this against: re-reading the same
questions at k=25 instead of the run's k=20 changed 22 verdicts in both
directions for a net of +6 (p = 0.29). A2's +26 is well clear of it.

## 5. Recovery on the failure classes this work owns

Counts are questions the definitive run got wrong that are correct in the arm.

| Class | n | C0 | A2 |
|---|---|---|---|
| single-hop, evidence never extracted | 34 | 1 | **18** |
| single-hop, evidence stored but not retrieved | 4 | 0 | 1 |
| multi-hop, evidence stored but not retrieved | 12 | 1 | 3 |
| multi-hop, evidence never extracted | 12 | 2 | 3 |
| single-hop, evidence already complete in context | 20 | 2 | 2 |
| multi-hop, evidence already complete in context | 13 | 2 | 4 |

The classes behave as the design predicts. The extraction gaps, where no stored
memory quotes the evidence, move only with the source-turn backstop; no read-path
change can retrieve a fact that was never written. The retrieval gaps move with
the roster. The "already complete" rows are the reader's own failures, held
constant here and owned by the reader workstream.

## 6. Why adversarial inflated, and whose problem it is

The seven adversarial questions A2 lost are all misattribution traps: the
question asks what Caroline said when Melanie said it, what Jon wanted for a
store that is Gina's, what Sam limited when it was Evan. Declining is correct.

Mapping each reader CHECK line onto the envelope's numbering, six of the seven
cite a **source turn**; the seventh cites a memory inside the baseline k=25
results and is therefore ordinary churn rather than an effect of this change. One
CHECK line states the misattribution outright and answers anyway ("the ginger
snap limit in [1]/[95] is Evan's, not Sam's").

A raw turn carries words without the attribution a typed memory's title supplies,
so a trap question finds matching words spoken by the other person. That is a
property of the backstop, and the decision to answer or decline on it is the
reader workstream's lever, not this one.

## 7. Standing against the pre-registered rules

| Rule | A2 |
|---|---|
| Non-adversarial accuracy rises, p < 0.05 | met, +26, p = 0.0002 |
| Adversarial falls by at most 3 net and not significantly | **failed on magnitude** (-6; p = 0.07) |
| No non-adversarial category loses more than 3 net | met, none lost |

A2 therefore does not ship as measured. The rule is applied as written rather
than reinterpreted now that the number is known.

## 8. Recommendation

Pending the A1 result, which isolates the roster.
