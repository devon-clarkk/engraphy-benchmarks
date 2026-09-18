# LoCoMo: diagnosis of the 2026-09-16 run and a recovery plan

Date: 2026-09-16
Runs compared: `fullrun-conv-20260916` (public engine `67dd41a`, schema 0024)
against `fullrun-conv-20260809` (engine `631e7be`, schema 0023, branch not in
the public repository).

Every number below is computed from the run artifacts in this repository and
from the unredacted outputs in the `engraphy-fresh-bench` worktree. Nothing here
changes a prompt, a threshold, or a question set.

## 1. Headline

The 2026-09-16 run scores **60.2% excluding adversarial** (234/389) and 63.2%
overall (316/500). The 2026-08-09 run scored 67.1% excluding adversarial.

Two findings dominate this report and they point in opposite directions.

1. **The decline against the August run is real.** It is caused by a 22.3%
   smaller memory store, and roughly half of it is recoverable by fixing write
   rejections that discard real facts over a date-format technicality.
2. **The comparison against Mem0 and Zep was not apples to apples.** Measured
   per category against the numbers those systems actually published, this run
   already beats Zep on three of four categories and leads both systems on
   temporal reasoning by a wide margin. The single headline figure understates
   the engine, because Engraphy grades itself under a materially stricter judge
   and a reader that is permitted to decline, against published figures produced
   under a generous judge, a prompt that forbids declining, and a larger
   retrieval budget. Re-measured on the same questions under conventions
   matching the published ones, this same run scores **roughly 77% excluding
   adversarial** against Mem0's published 66.88 (section 6).

Both statements are true at once, and the second is the one that should change
how the number is presented.

## 2. Comparability: what Mem0 and Zep actually measure

The Mem0 paper reports LoCoMo per category under an LLM-as-judge metric
(Table 1). Set beside this run:

| Category | Engraphy 2026-09-16 | Mem0 | Mem0g | Zep |
|---|---|---|---|---|
| Single-hop | 63.6 | 67.13 | 65.71 | 61.70 |
| Multi-hop | 43.8 | 51.15 | 47.19 | 41.35 |
| Temporal | **67.7** | 55.51 | 58.13 | 49.31 |
| Open-domain | 57.7 | 72.93 | 75.71 | 76.60 |

Engraphy is ahead of Zep on single-hop, multi-hop and temporal, and ahead of
both published systems on temporal reasoning by 12.2 points over Mem0 and 18.4
over Zep. One caveat on the Zep column: those are Mem0's measurement of Zep, and
Zep disputes it as a misconfiguration, so "ahead of Zep" rests on a competitor's
contested measurement of a competitor and should be said with that attached. The
comparison against Mem0's own figures carries no such problem.

Engraphy trails on open-domain-knowledge, which is 26 questions in this
sample and is the one category that does not depend on stored conversation
memories at all. It scored 57.7% in both runs, unchanged, so it is not part of
the regression and is a separate, smaller problem.

Four methodology differences separate the harnesses. Each is documented, and
each moves the number in the same direction.

**Adversarial questions are excluded from the published figures.** The Mem0
paper removes the category because ground truth answers were unavailable and the
expected behaviour is that the agent recognises the questions as unanswerable.
Engraphy reports its adversarial result openly. Quoting the 60.2% figure
excluding adversarial is therefore the correct basis for comparison, and it is
already the figure in use.

**The reference answer prompt forbids declining.** Read from the source, the
`mem0ai/memory-benchmarks` LoCoMo prompts instruct the reader to "NEVER say 'not
specified', 'not mentioned', 'no record', or 'the memories don't say'", to give
the best answer from available evidence with "No hedging, no caveats", and never
to return an empty answer when relevant memories exist. The same file confirms
`CATEGORIES_TO_EVALUATE = [1, 2, 3, 4]`, excluding adversarial.
Engraphy's reader prompt (`bench/prompts/read.md`, rule 2) does the opposite: it
instructs the reader to reply `INSUFFICIENT` when the memory does not contain
the answer, and states that declining is the correct response. Engraphy's judge
then scores every `INSUFFICIENT` as wrong. **This run declined on 76 of the 389
non-adversarial questions and was scored wrong on all 76, which is 19.5 points
of the benchmark.**

**The judge rubrics differ sharply on partial answers.** The reference judge
prompt awards partial credit explicitly: mark CORRECT if the answer includes "AT
LEAST ONE correct item from the gold answer's list", "Dates within 14 days of
each other are CORRECT. Durations within 50% are CORRECT", and never penalise a
longer answer that carries the gold facts plus more. Engraphy's judge
(`bench/prompts/judge.md`) requires every item of a multi-item gold answer to be
present and states that no partial credit is given. **24 of the 79
answered-and-wrong non-adversarial failures in this run were marked wrong solely
for omitting one item from a multi-item gold list**, which is 6.2 points. A
concrete case: gold "beach, mountains, forest", Engraphy answered "In forests
and in the mountains", graded wrong 3-0.

**The retrieval budget differs, though the comparison is not clean.** Mem0's
current evaluation documentation describes a top-200 retrieval budget on a
single-pass setup, and that documentation describes the configuration behind the
92.5 figure, not the paper's 66.88. The paper itself does not state Mem0's
retrieval budget. So the honest statement is that this Engraphy arm retrieves
**10 results**, the current reference suite uses 200, and the budget behind the
66.88 figure is undocumented. Do not pair the docs' budget with the paper's
accuracy.

A fifth difference affects confidence rather than level: the Mem0 paper reports
the mean of 10 independent runs with a standard deviation. Engraphy reports a
single run. Per-question churn between two nominally identical Engraphy runs is
19.6% (98 of 500 questions flipped verdict), so a single-run figure carries more
uncertainty than the 95% Wilson interval alone suggests.

**The denominator differs, and this one cuts against Engraphy.** The published
figures are computed over all ten LoCoMo conversations. Engraphy's 500-question
sample covers three of them (conv-26, conv-30, conv-49). The two numbers are
therefore not drawn from the same population, and no amount of convention
matching fixes that. It is the one comparability axis that is not in Engraphy's
favour, and it should be stated wherever the comparison is made.

The published numbers are themselves contested. Zep's 84% claim was recomputed
by Mem0 at 58.44% after removing adversarial questions, and Zep rebutted with a
corrected 75.14%: a 26-point spread on one system depending on who ran the
harness. Any single vendor number, Engraphy's included, should be quoted with
its configuration attached.

### What this means for the pitch

The honest framing is not "we are 10% behind". It is: under a stricter judge, a
reader allowed to say it does not know, and a retrieval budget of 10 results,
Engraphy is competitive on single-hop and multi-hop, leads both published
systems on temporal reasoning, and trails on open-domain knowledge.
Section 5 recommends publishing two clearly labelled numbers, the strict one and
one computed under the reference harness's own conventions, and leading with the
per-category table rather than a single scalar.

## 3. Root cause of the decline against the August run

### 3.1 The decline is real, and it is not the judge

McNemar paired tests on the same 500 questions:

| Set | n | lost | gained | chi2 | p |
|---|---|---|---|---|---|
| All | 500 | 70 | 28 | 17.15 | 0.00003 |
| Non-adversarial | 389 | 53 | 26 | 8.56 | 0.00344 |
| Adversarial | 111 | 17 | 2 | 10.32 | 0.00132 |

The judge is not the cause. On the 53 lost non-adversarial questions the new run
judged 51 as unanimous 0-3 wrong and the old run judged 52 as unanimous 3-0
correct. Split 2-1 verdicts are 2.0% of all 500 questions. The answers genuinely
got worse.

### 3.2 The causal chain

Every loss sits downstream of a different store. **0 of 500 retrieval envelopes
were byte-identical between the two runs.** Envelope size barely moved (-1.1% on
the lost set), so it is context content that changed, not context volume.

The store shrank from 346 nodes to 269, a 22.3% reduction, from two independent
causes that must not be averaged together:

- **34 fewer drafts extracted** (348 to 314) despite an identical `extract.md`
  prompt hash `b7fdf557f7f60a9c` and the same model. Extraction is stochastic
  and is a confound in this comparison, not a regression that was shipped.
- **43 more write rejections** (2 to 45).

Retrieval then degraded measurably on the lost set. Paired `gold_in_context`
fraction on the 53 lost questions: mean 0.870 to 0.568, with 23 strictly worse,
28 unchanged, none better. The gained set moved the other way (0.652 to 0.879).
The stable-correct set barely moved (0.891 to 0.881).

### 3.3 The 45 write rejections, classified

The brief asked to separate correctly rejected junk from real facts lost to a
format technicality. The rejection messages make this unambiguous.

**31 date-format rejections (69%), all real facts lost.** Every one is a
relative or partial time expression that the attribute spec requires to be a
date. The SQL trigger `nodes_validate_attrs_fn` raises `attrs.as_of must be a
date`, and because it is a trigger the **entire node write fails, not just the
offending attribute**. Examples taken verbatim from the run log:

- "Caroline is transgender, began transitioning three years ago"
- "Caroline moved from her home country four years ago"
- "Melanie married her husband five years ago"
- "Gina lost her DoorDash job in January 2023" (month precision, a real date)
- "Evan drove to Banff and went skiing last month"
- "Sam decided to take up painting to de-stress"

These are not junk. They are facts whose time attribute is imprecise, which is
the normal case in conversation.

**7 cross-type supersession rejections, a modeling error correctly refused.**
The message reads that the type must equal the superseded node's type and that
cross-type supersession is a modeling error. The engine is right to refuse this.
The defect is the consequence: the replacement is discarded entirely rather than
inserted as a new node, so a correct refusal still destroys a real fact.

**7 `SupersedeUnresolvedBandError`, an unhandled case.** The replacement banded
`needs_confirmation` against a node other than `old_id` and the plan does not
define this case. Also a real fact lost, and the error text says the case is
known and unspecified.

### 3.4 Write rejections traced to specific wrong answers

Three rejections link directly to questions this run got wrong, confirming the
mechanism rather than inferring it:

| Question | Gold | Answer given | Rejected node |
|---|---|---|---|
| conv-49:q113 "What did Evan suggest Sam try as a calming hobby?" | Painting | "Picking up a hobby to de-stress." | "Sam decided to take up painting to de-stress" (cross-type supersede) |
| conv-49:q109 "What fun activity did Evan mention doing in July 2023?" | skiing | INSUFFICIENT | "Evan drove to Banff and went skiing last month" (date) |
| conv-26:q11 "Where did Caroline move from 4 years ago?" | Sweden | INSUFFICIENT | "Caroline moved from her home country four years ago" (date) |

In each case the surviving context carries the topic but not the bridging fact.
For q109 the store retained "Evan enjoys skiing, snowboarding, and ice skating"
but not the dated event, so the reader could not place it in July 2023 and
correctly declined. **The reader behaved properly; the write path had destroyed
the evidence.**

### 3.5 Adversarial: the obvious hypothesis is false

All 15 net adversarial losses are `reader-over-answered` (14 to 29). The
standing hypothesis was that a sparser store returns more marginal context under
fixed-k retrieval, tempting the reader to construct an answer, and that a
relevance floor would fix it. **The data falsifies this.**

| Group | n | mean top similarity |
|---|---|---|
| Adversarial, correctly declined | 82 | 0.7413 |
| Adversarial, over-answered | 29 | **0.7748** |
| Non-adversarial, correct | 234 | 0.8096 |
| Non-adversarial, wrong | 155 | 0.7773 |

Over-answered adversarial questions have *higher* top similarity than correctly
declined ones. The reader is not being tempted by weak context, it is being
tempted by context that looks strong and is topically adjacent.

A relevance floor is also a bad trade on its own numbers. A floor at 0.80 would
catch 20 of the 29 over-answers but puts **35% of currently correct
non-adversarial answers at risk**; at 0.82 it reaches 24 of 29 but risks 48%.
This lever should not be built.

### 3.6 The harness failure taxonomy overstates reader failure

`bench/core/diagnostics.py` labels 85 of the 155 non-adversarial failures
`reader-miss`. That bucket rests on a keyword-overlap heuristic which the module
docstring itself calls "not ground truth", and manual review confirms it is
inflated. Of the 24 failures where the reader declined with gold words clearly
present in a retrieved node, hand classification gives roughly:

- ~9 genuine reader over-abstention, where the answer is plainly stated (for
  example conv-30:q58, where the rank-1 node is titled "Jon shut down his bank
  account for his business" and the reader still answered INSUFFICIENT);
- ~3 caused by a write rejection destroying the bridging fact (section 3.4);
- ~11 heuristic false positives, where the gold words appear on a different
  person or a different event (conv-26:q94 asks about Melanie's hand-painted
  bowl and the context holds Caroline's; conv-26:q63 asks about a talent show
  and the context holds an art show in the same month).

The true reader bucket is therefore smaller than the harness reports and the
store and retrieval bucket is larger. The recovery plan is ranked on the
corrected reading, not on the harness labels.

### 3.7 Bucket table

Measured across all 155 non-adversarial failures, by whether the gold fact is
present in a single retrieved node:

| Bucket | n | pp of the 389 | Corrected reading |
|---|---|---|---|
| Gold absent from context | 57 | 14.7 | store and retrieval |
| Gold partially in context | 45 | 11.6 | mixed, mostly store |
| Answered wrong with gold in context | 21 | 5.4 | reader and judge strictness |
| Declined with gold in context | 24 | 6.2 | ~9 reader, ~3 write path, ~11 heuristic false positive |
| Gold not scorable (short or numeric gold) | 8 | 2.1 | unattributable |

Cross-cutting, and the single largest actionable figure: **the reader declined
on 76 of 389 non-adversarial questions and was scored wrong on every one, 19.5
points.**

## 4. Levers, ranked

Estimates are honest ranges, not targets. Nothing here tunes to LoCoMo: no
question is inspected to set a threshold, no prompt is fitted to the test set,
and every change is a general engine or harness improvement that would apply to
any corpus.

| # | Lever | Est. honest gain (excl adv) | Effort | Risk |
|---|---|---|---|---|
| 1 | Port the never-drop-node write path to the public engine | +4 to +7 pp | Low, already built | Low |
| 2 | Publish per-category results and a reference-convention number alongside the strict one | 0 pp, but corrects the comparison | Low | Low, provided both are labelled |
| 3 | Fix reader abstention discrimination, both directions | +4 to +5 pp measured, non-adv | Medium | Medium |
| 4 | Raise the retrieval budget above k=10 and state why | +1 to +3 pp | Low | Low |
| 5 | Report a mean of N runs rather than a single run | 0 pp, removes 19.6% churn from the headline | Medium | Low |
| 6 | Relevance floor on retrieval | negative | n/a | Rejected, see 3.5 |
| 7 | Reranking | none available | n/a | Already measured and rejected |

**Lever 1 is a port, not a build.** Every write-path defect in section 3.3 was
already diagnosed and fixed on the Engram branch
`feature/never-drop-node-flexible-dates`, and the fix never reached the public
engine. It has three parts, all at engine level:

- date attributes accept `YYYY`, `YYYY-MM` and `YYYY-MM-DD`, stored verbatim and
  never coerced, which is precisely the LoCoMo failure class;
- an invalid value of a declared attribute is quarantined and **the node and its
  valid attributes are kept**, with `dropped_attrs` surfaced in the write
  envelope so the loss is loud rather than silent;
- cross-type supersede and the fail-closed supersede-band case both downgrade to
  a plain write with an explicit `supersede_downgraded` flag. The original guard
  was fail-closed to avoid a silent half-supersede, not because the memory had to
  be destroyed, and an explicit flag preserves the memory while keeping
  non-completion loud.

Verified absent from the public engine on 2026-09-16: `engraphy/core/attr_spec.py`
still calls `datetime.date.fromisoformat` behind a full-date regex, and
`dropped_attrs`, `quarantine` and `supersede_downgraded` appear nowhere in
`engraphy/`.

That branch measured write-yield at **99.4% (346/348)** live on these same three
conversations, against **85.7% (269/314)** here, and an LLM-free replay of logged
rejected drafts recovered 30 of 30. This is the highest-confidence lever in the
plan because the fix is written and its effect is already measured, and it is a
real engine improvement rather than a benchmark accommodation: any deployment
ingesting conversation hits this wall, because people say "last month", not
"2023-08-14".

**Levers 6 and 7 are closed, and the evidence is worth keeping.** The relevance
floor is refuted in section 3.5. Reranking was commissioned earlier precisely
because `reader-miss` looked dominant, was built as a node-distance reranker and
measured credit-free with a rank-of-gold metric, and was rejected: recall@5 and
recall@10 both fell, multi-hop skewed negative, and roughly 92% of reader-miss
golds were already ranked at or above rank 3. This run independently reproduces
that: among the losses where the gold-bearing node is in context, its **median
rank is 1**. Nothing a reranker can reach.

**Lever 3, abstention discrimination.** The reader declines on answerable
questions and answers unanswerable ones. That is not a threshold set too high or
too low, it is a failure to distinguish "the context contains the specific fact
asked for" from "the context is topically related", which is why the similarity
data in 3.5 shows no separation. Section 6 measures the size of one half of it:
forcing a commit recovers 15 to 19 questions **under the unchanged strict
judge**, 4 to 5 points, all of them questions where the reader already had what
it needed. The goal is not to force commitment, which would forfeit the
adversarial category, but to make the reader's decline decision track whether the
specific fact is present. This is the honest capability gap and it is worth
attacking on its own merits, not because LoCoMo rewards it.

**Lever 4, retrieval budget.** k=10 against a documented top-200 in the
reference harness. Pick k for a stated reason and report what it does once. Do
not sweep k against the LoCoMo score.

## 5. Best honest number believed achievable

Against the current strict rubric and reader stance, levers 1, 3 and 4 plausibly
land **66 to 71% excluding adversarial**, with the write-path port carrying most
of it. That is an estimate from bucket sizes and from the write-yield the port
already demonstrated, not a measurement of the combined result, and it should not
be quoted until a run confirms it.

Reported under the same conventions the published Mem0 and Zep figures use, the
existing run already scores **roughly 77% excluding adversarial** (firm floor 75.6%, ceiling
78.9%), measured in section 6 rather than asserted. That is above Mem0's
published 66.88, on a retrieval budget of 10 results.

Combining the two: with the write path fixed and the results reported under
matched conventions, the defensible claim is a figure in the high seventies with
the strict-convention figure published beside it. No part of that requires
tuning to LoCoMo.

The recommendation is to publish both, clearly labelled, and to lead with the
per-category table. Engraphy leading both published systems on temporal
reasoning is a stronger and more defensible claim than any single scalar.

## 6. Targeted experiment: the reference-convention number

Run 2026-09-16. Two arms, no new retrieval, no question selection, no prompt
fitted to any question.

**Arm A.** The 76 declined non-adversarial questions were re-read from their
saved envelopes under a commit-forcing reader prompt mirroring the reference
harness convention (never decline, commit and answer). Engraphy's
answer-discipline skill is deliberately not loaded in this arm, because the
point is to reproduce the reference convention rather than blend the two.

**Arm B.** The 79 answered-and-wrong non-adversarial questions were re-graded
under a rubric carrying the reference judge's stated tolerances: any one item of
a multi-item gold list counts, dates within roughly two weeks count, durations
within roughly 50% count, and the gold answer is used only to accept.

### 6.1 Results

| Configuration | Score, non-adversarial (n=389) |
|---|---|
| As published: strict judge, reader may decline | 234/389 = **60.2%** |
| Commit stance, strict judge | 249-253/389 = **64.0-65.0%** |
| Reader may decline, generous judge | 279/389 = **71.7%** |
| Commit stance + generous judge (reference conventions) | 303-307/389 = **77.9-78.9%** |

Arm A was run twice (the second pass was incidental), giving 19 and 15 recovered
questions under the strict judge and 28 and 24 under the generous judge. The
ranges above are those two passes. Arm B was identical on both passes at 45 of
79 flips. The spread is reader stochasticity and is consistent with the 19.6%
per-question churn measured in section 2. Only the second pass was kept on disk,
so the point estimate is sound but there is no stable identified set of
"winnable" questions to name.

Two structural notes on the combined row. The 79 already-answered questions were
not re-read under the commit stance, so that row mixes answers produced under
one stance with answers produced under another. This is defensible because those
questions had already committed to an answer, which is what the commit stance
asks for, but it is not a single clean configuration. And the commit stance was
applied only to non-adversarial questions, since applying it to adversarial ones
would be pointless (see 6.3).

### 6.2 Validity controls on the generous rubric

A permissive rubric is only meaningful if it still rejects wrong answers. Two
controls, because the first tests an easier population than the one that
actually drives the gain.

**Control 1, mismatched answers.** Sixty questions the run answered correctly
were re-paired with the answer given to a *different* question from the same
conversation, so every pair is wrong by construction, and both rubrics graded
the identical set:

| Rubric | Accepts deliberately mismatched answers |
|---|---|
| Engraphy strict | 2/60 = 3% |
| Reference-style generous | 5/60 = 8% |

**Control 2, the confabulation population.** Control 1 pairs a question with an
answer about a different topic, which is easy to reject. The population that
matters is different in kind: on the questions where the gold fact was *not* in
context, the commit-forcing stance obliges the reader to construct an answer
from topically adjacent context about the right person, which is exactly what a
partial-credit rubric might wave through. Splitting Arm A by whether the gold
fact was present:

| Gold fact in the retrieved context | n | Strict accepts | Generous accepts |
|---|---|---|---|
| Clearly present (overlap >= 0.60) | 24 | 11 (46%) | 12 (50%) |
| Partly present | 18 | 1 (6%) | 5 (28%) |
| Absent (overlap < 0.30) | 28 | 2 (7%) | 5 (18%) |
| Not scorable | 6 | 1 | 2 |

The gain is concentrated where it should be. Where the reader genuinely had the
answer and declined anyway, forcing a commit recovers about half the questions,
and the strict judge accepts almost as many as the generous one (11 against 12),
so that recovery is not a grading artifact. Where the gold fact was absent, the
generous rubric accepts 18%, above the 8% mismatched-answer floor but far from a
rubber stamp.

**The honest discount.** Of the 303-307 total, 234 is the base, 45 is Arm B
(real answers marked wrong only for incompleteness, which the reference rubric
accepts by an explicitly stated rule), and 15-19 is Arm A under the **unchanged
strict judge**, which is a capability finding independent of any rubric change.
That subtotal is 294-298, or **75.6 to 76.6%**, and it is the firmest part of
the figure. The remaining ~9 are Arm A answers only the generous rubric
accepted; inspection shows most rest on rules the reference judge states
literally (gold "2" answered "once or twice"; gold 19 October answered "the
weekend before 20 October", inside the stated 14-day tolerance), while a few are
hedged lists that happened to contain one gold item. **Treat the
reference-convention figure as roughly 77%, with 78.9% as the ceiling and 75.6%
as the floor.**

One rule was not reproduced: the reference judge also marks an answer WRONG when
supplied evidence does not support it. No evidence was supplied to either rubric
here, so that check was inert, which makes this reconstruction slightly more
permissive than the reference on that one axis.

### 6.3 What this does and does not establish

It establishes that **the gap to the published Mem0 figure was methodology, not
memory quality.** Mem0's paper reports 66.88 overall under its LLM-as-judge
metric. Engraphy, on the same question set under conventions matching the
published ones, scores roughly 77%, and it does so on a retrieval budget of 10
results.

It also isolates one honest capability gain that owes nothing to the judge:
**under the strict judge alone, the commit stance recovers 15 to 19 questions,
4 to 5 points.** Those are questions where the reader had enough in context and
declined anyway. That is lever 4 and it is real.

Three caveats, stated plainly.

1. The generous rubric reproduces the reference judge's stated tolerances, which
   were read from the `mem0ai/memory-benchmarks` source and match it closely
   (at-least-one-item, 14-day dates, 50% durations, no penalty for extra
   detail). It is still a reconstruction rather than the literal prompt, and
   this experiment did not run Mem0's harness end to end. Label the figure
   "under a rubric matching the published tolerances", never "measured under
   Mem0's harness".
2. **The commit stance destroys adversarial performance by construction.** A
   reader that can never decline cannot pass a category whose correct answer is
   to decline. The reference conventions exclude that category, which is exactly
   why the trade is invisible in the published numbers. Engraphy measures both,
   and that is a genuine differentiator rather than a deficit.
3. The ~77% figure is a single measurement on one run of a store that is itself
   22.3% smaller than it should be. Fixing the write path (levers 2 and 3) is
   still worth doing, and would raise both the strict and the reference-
   convention numbers.

### 6.4 Recommended reporting

Publish three numbers, each labelled with its configuration, and lead with the
per-category table from section 2:

- **60.2% excluding adversarial**, strict judge, reader permitted to decline,
  k=10. Engraphy's own conventions, the conservative figure.
- **73.9% adversarial**, the category the published comparisons exclude.
- **~77% excluding adversarial** (floor 75.6%, ceiling 78.9%) under conventions
  matching the published ones, with the reconstruction caveat attached.

Leading with "60.2%" against a competitor's "66.88%" compares two different
measurements and understates the engine. Leading with "~77%" alone would
overstate it. The pair, with the configuration attached and the adversarial
result shown, is both truthful and stronger than either alone.

**The standing rule still holds: level with the leaders, not ahead of them.**
The three-of-ten-conversations denominator (section 2) means a point estimate
above Mem0's published figure does not establish a win, and the existing rule
recorded on 2026-08-28 for public surfaces should not be relaxed on the strength
of this experiment. What this work changes is the strength of the "level"
claim, not its direction: the gap that looked like a ten-point capability
deficit is measured here as a methodology artifact, and the one category that
clears its comparator outright remains temporal reasoning.
