# LoCoMo open-domain: failure analysis, the competitor finding, and levers

Date: 2026-09-19
Run analysed: `locomo-definitive-20260917` (engine `3df1a4d`, arm
`llm-conversational/search_only/always_distinct/k20`, reader `claude-opus-4-8`
with the `verify` contract, judge `claude-sonnet-5` best of 3). Unredacted
outputs read from `engraphy-public-levers/runs/locomo-definitive-20260917`,
including the reference-convention pass under `reference/`.

Read-only analysis. No engine, harness, prompt or published result was changed.

## 1. Headline

The question was why open-domain-knowledge, at 69.2% (18/26) strict, trails
Mem0 (72.93), Mem0-graph (75.71) and Zep (76.60). Two findings answer it.

1. **The Mem0 paper's category columns do not match LoCoMo's category numbers.**
   Its "open-domain" column is LoCoMo category 4, which is single-hop factual
   lookup. Its "multi-hop" column is LoCoMo category 3, which is Engraphy's
   open-domain category. Aligned correctly, Engraphy's open-domain result is
   compared against **51.15 (Mem0), 47.19 (Mem0-graph) and 41.35 (Zep)**, and
   Engraphy leads all three by 18 to 28 points under its own stricter judge.
   Section 3 shows the evidence, which is arithmetic from the paper's own
   tables and holds to within 0.01 points across five systems.
2. **The eight open-domain failures are mostly grading, not memory.** Four are
   substantively right answers failed by the strict judge on a multi-part
   synthesized gold. None is a decline. None needs world knowledge the memory
   lacks. One is a genuine extraction miss, one a retrieval miss, one a reader
   aggregation miss, one a subjective call.

The consequence runs both ways. The realignment also moves Engraphy's real
deficits to **multi-hop** (category 1) and **single-hop** (category 4), where
published comparisons currently show Engraphy ahead. Section 5 gives the
corrected table, and section 6 redirects the levers to where the gap actually
is.

## 2. Why Engraphy loses open-domain questions

Category 3 questions are commonsense inferences over the conversation: "Would
Caroline likely have Dr. Seuss books on her bookshelf?", "Would Melanie go on
another roadtrip soon?". Each needs the conversational facts plus a reasoned or
world-knowledge step.

### 2.1 Method

For each of the 26 questions: the strict verdict and its reason, the reader's
answer and CHECK line, whether it declined, the reference-convention verdict,
and **evidence recall**: the fraction of the question's LoCoMo evidence turns
whose text (first 60 normalised characters, the `bench.k_sweep.recall`
definition) appears in a retrieved memory body. "In seen store" is the same
test against the union of every memory retrieved for any of the 500 questions
in that conversation, a lower bound on what the store holds. The store itself
could not be queried: the database credentials are not in this environment and
were not sought.

### 2.2 The eight failures

Each question is 3.8 points of the category and 0.26 points of the 389
non-adversarial questions.

| Question | Gold | Engraphy answered | Evidence recall (in seen store) | Reference judge | Cause |
|---|---|---|---|---|---|
| conv-26:q2 fields Caroline would pursue in education | Psychology, counseling certification | Counseling and mental health | 1.0 (1.0) | accepts | Judge strictness: "psychology" is the annotator's inference, not in the conversation |
| conv-49:q19 advice Evan and Sam would give on a life transition | small changes; hiking, painting, road trips; friendship and support | small consistent changes; lean on supportive people; reframe setbacks | 0.18 (0.36) | accepts | Judge strictness on a three-part synthesized gold, plus thin coverage of 11 evidence turns |
| conv-49:q31 how health changes shape their approach to stress | challenges as growth; proactive | patience, persistence, mutual encouragement | 0.33 (0.33) | accepts | Judge strictness on an abstract paraphrase |
| conv-49:q51 Sam's challenges and how he addresses them | motivation, diet; cooking classes, support from friends like Evan | long, accurate list omitting "support from Evan" | 0.0 (0.5) | accepts | Judge strictness (one omitted item), plus the support turn not retrieved |
| conv-26:q59 would Caroline be considered religious | Somewhat, not extremely | Probably not in a formal sense, loosely spiritual at most | 1.0 (1.0) | accepts | Reader calibration on a subjective inference; strict judge split 1-2 |
| conv-49:q43 how often Sam gets checkups | every three months | no regular cadence recorded | 1.0 (1.0) | rejects | Reader did not aggregate three dated checkups that were all in context |
| conv-49:q20 gift for both Evan and Sam's healthy lifestyles | cookbook or meal delivery | fitness tracker | 0.18 (0.71) | rejects | Retrieval: the diet and recipe turns are in the store but were not surfaced |
| conv-26:q69 traits Melanie might say Caroline has | thoughtful, authentic, driven | brave, resilient, compassionate, determined | 0.0 (0.0) | accepts | Extraction miss: Melanie's compliments were never stored |

Notes on the contestable ones, stated so no cause is overclaimed:

- **q43.** The checkups fall in sessions dated 24 May, 15 August and 8 October
  2023, twelve and eight weeks apart, and in January 2024 Sam says he has not
  seen a doctor in a while. The reader answered from the latest statement. The
  gold is an annotator's inference from session spacing and is debatable.
- **q20.** Only 3 of the 17 evidence turns were retrieved, although at least 12
  are in the store. The three retrieved were the fitness-routine and
  progress-tracker turns, which is what the reader answered from. The salad,
  recipe, stir-fry and snack-swap turns (D3:3, D3:5, D4:10, D8:7, D8:12) are in
  the store and were not retrieved. Counted as a retrieval miss.
- **q69.** The gold traits paraphrase three things Melanie says to Caroline:
  "you're so thoughtful", "you really care about being real", "your drive to
  help is awesome". None appears in any memory retrieved for any question in
  the conversation. That is strong evidence the extractor did not keep
  compliments one speaker pays another, but it is a lower bound, not a store
  query.

### 2.3 Bucket totals

The measured fact comes first: re-read and graded under the reference
conventions, **6 of the 8 failures are accepted**, and the category moves from
18/26 to 23/26 defensible on a rubric change alone. So most of the category's
loss is rubric-dependent. The per-question reading in 2.2 is the supporting
evidence for which six those are and why, not the basis of the claim.

| Bucket | n | pp of category | pp of 389 |
|---|---|---|---|
| Rubric-dependent: strict judge rejects a synthesized or multi-part answer the reference judge accepts | 4 | 15.4 | 1.0 |
| Reader calibration on a subjective inference | 1 | 3.8 | 0.3 |
| Reader aggregation miss, evidence all in context | 1 | 3.8 | 0.3 |
| Retrieval miss, evidence in store | 1 | 3.8 | 0.3 |
| Extraction miss | 1 | 3.8 | 0.3 |
| Reader declined | 0 | 0 | 0 |
| Needed world knowledge the memory does not hold | 0 | 0 | 0 |

The world-knowledge bucket is empty for a reason worth recording: the reader
already combines memory with general knowledge correctly. Among the 18 wins are
"Jasper and the Icefields Parkway" to Canada, "Lake Tahoe" to California, "a
fan of Bach and Mozart" to enjoying Vivaldi, "married in December" to
Christmas, and "kids' classics" to Dr. Seuss. The grounded stance permits a
sourced inference, and it is working.

Under the reference judge the category is 88.5% defensible (23/26). The strict
judge alone accounts for four to five of the eight failures.

### 2.4 How big the gap ever was

Even taken at face value, 18 of 26 against Mem0's 72.93 is a one-question gap,
and against Zep's 76.60 a two-question gap. The 95% interval on 18/26 is 50 to
84. On three conversations this category cannot distinguish any of these
systems.

The reader alone does not carry this category. In July, the same-family Opus
reader over the untyped verbatim floor scored 30.8% on these 26 questions, and
46.2% over typed extraction (`Engram/runs/published/locomo-3conv-opus-2026-07-22`).
Reader stance and rendering have changed since, so this is not a clean
decomposition, but the store clearly matters.

## 3. The finding: the Mem0 paper's columns are mislabeled

### 3.1 The evidence

The Mem0 paper (arXiv:2504.19413) reports per-category LLM-judge scores in
Table 1 under the column names Single-Hop, Multi-Hop, Open-Domain and Temporal,
and an overall score in Table 2. LoCoMo's four scored categories have fixed
sizes in the dataset: category 1 has 282 questions, 2 has 321, 3 has 96 and 4
has 841, 1,540 in all.

The overall score is the question-weighted mean of the four categories. There
are 24 ways to assign the four column names to the four category numbers. For
each, the Table 1 columns were weighted by those counts and compared with the
Table 2 overall, for every system reported in both tables:

| Assignment of paper columns to LoCoMo categories | Mem0 | Mem0g | Zep | LangMem | OpenAI |
|---|---|---|---|---|---|
| Single-Hop=1, Temporal=2, **Multi-Hop=3, Open-Domain=4** | -0.00 | -0.00 | -0.00 | +0.01 | -0.00 |
| Next best (Single-Hop=2, Temporal=1, Multi-Hop=3, Open-Domain=4) | +0.29 | +0.19 | +0.31 | +0.99 | +1.06 |
| Names as the dataset defines them (Multi-Hop=1, Temporal=2, Open-Domain=3, Single-Hop=4) | -4.74 | -7.08 | -9.67 | -6.02 | -1.80 |

The test has 24 candidate assignments and five independent constraints, one
per system. Because the four category sizes are all different, each assignment
predicts a distinct overall figure, so the assignment is identifiable. The best
fit reproduces all five published overall figures with a largest error of 0.01
points and a summed absolute error of 0.02. The runner-up has a largest error
of 1.06 and a summed error of 2.84, over a hundred times worse. Taking the
column names at face value, as the dataset defines them, misses by 1.8 to 9.7
points per system.

The assignment is a permutation, not a relabelled ordering. Reading Table 1
left to right, Single-Hop, Multi-Hop, Open-Domain and Temporal hold LoCoMo
categories 1, 3, 4 and 2. So the columns are neither in dataset-ID order nor in
dataset-name order; two headers are swapped relative to the data they hold.

Two further checks agree:

- **The paper's own definitions contradict its columns.** It defines single-hop
  as "locating a single factual span contained within one dialogue turn". That
  is the shape of category 4, whose questions average 1.07 evidence turns. Its
  "Single-Hop" column is category 1, which averages 3.13 evidence turns with 98%
  multi-evidence.
- **Mem0's current harness uses the dataset's names.** `mem0ai/memory-benchmarks`
  at `4b61c5d`, `benchmarks/locomo/prompts.py`, defines
  `CATEGORY_NAMES = {1: "multi-hop", 2: "temporal", 3: "open-domain", 4: "single-hop", 5: "adversarial"}`.
  That matches the dataset and Engraphy's loader, and disagrees with the paper.

Mismatches between the LoCoMo white paper's category descriptions and the
dataset's category IDs have been noted by others. The assignment the Mem0 paper
used does not match either the dataset's names or any single documented
alternative ordering; it is established here only by the arithmetic above.

### 3.2 What it means for this question

The paper's "open-domain" figures (72.93, 75.71, 76.60) are single-hop factual
lookups, the largest and easiest category. The paper's figures for the
category Engraphy calls open-domain are in its "multi-hop" column: Mem0 51.15,
Mem0-graph 47.19, Zep 41.35.

### 3.3 How Mem0-graph and Zep do on each category, correctly read

**Mem0-graph is not strong on open-domain.** On LoCoMo category 3 it scores
47.19, *below* base Mem0's 51.15. Its graph adds nothing to commonsense
inference questions and costs about four points. Where it is strong, 75.71, is
category 4, single-turn factual lookup.

Why graph memory suits category 4, from the primary sources:

- **Mem0-graph** extracts entities and (source, relation, destination) triplets
  with an LLM, resolves new entities against existing nodes by embedding
  similarity, marks conflicting relationships invalid rather than deleting
  them, and retrieves two ways: entity-centric (find the query's entities, walk
  their incoming and outgoing relations) and semantic triplet matching
  (arXiv:2504.19413, section on Mem0g). A single-turn fact such as "what was
  grandma's gift to Caroline" becomes one precise triplet, which is exactly what
  those two retrievers find.
- **Zep / Graphiti** keeps a non-lossy episode subgraph beneath an entity
  subgraph and a community subgraph, resolves entities with embedding plus
  full-text candidates and an LLM, stores bi-temporal edges, retrieves by
  cosine, BM25 and breadth-first search, reranks by RRF, MMR, episode mentions,
  node distance or cross-encoder, and hands the reader facts with their
  validity dates (arXiv:2501.13956). The Zep paper does not evaluate on LoCoMo;
  every Zep LoCoMo number is Mem0's measurement or Zep's rebuttal, and Zep's
  rebuttal publishes only an overall 75.14%.

What the Mem0 paper's answer prompt does on inference questions is also
relevant: it instructs the reader to "Focus only on the content of the
memories". Engraphy's grounded stance permits a sourced inference, and the
reader visibly uses it on category 3. That is a plausible contributor to
Engraphy's lead here, but it is confounded with the reader model (Claude Opus
4.8 against GPT-4o-mini) and cannot be separated from it with the data
available.

## 4. What this changes in the published comparison

**The headline survives intact.** 66.8% excluding adversarial against Mem0's
66.88 is a comparison of overall figures and does not depend on category
labels. The temporal claim, 72.9 against a best published 58.13, also survives,
because the paper's Temporal column is category 2 either way.

**Two per-category claims are now wrong and must be corrected.** Any surface
that sets Engraphy's single-hop 69.0 beside Mem0's 67.13, or its multi-hop 53.8
beside 51.15, 47.19 and 41.35, is comparing different categories. Correctly
aligned, both are deficits. The house rule that public copy states only what is
currently true makes this a required correction, not an option. The places
found carrying the column-name comparison:

- `analysis/2026-09-18-locomo-definitive-results.md`, section 1 table;
- the per-category line of the proj-engraphy note for the definitive run;
- any engraphy.tech comparison copy or release-notes text that quotes
  per-category comparisons (the v0.3.0 notes quote the headline and temporal
  figures, which are unaffected; other per-category text was not audited here).

The recorded caveat "category mapping unstated" can now be replaced by the
mapping itself.

## 5. The corrected per-category comparison

| LoCoMo category (dataset) | Engraphy strict | Engraphy reference, defensible | Paper column that holds it | Mem0 | Mem0g | Zep |
|---|---|---|---|---|---|---|
| 1 multi-hop | 53.8 (43/80) | 93.8 | "Single-Hop" | 67.13 | 65.71 | 61.70 |
| 2 temporal | **72.9** (70/96) | 89.6 | "Temporal" | 55.51 | 58.13 | 49.31 |
| 3 open-domain | **69.2** (18/26) | 88.5 | "Multi-Hop" | 51.15 | 47.19 | 41.35 |
| 4 single-hop | 69.0 (129/187) | 80.7 | "Open-Domain" | 72.93 | 75.71 | 76.60 |

Read under the strict judge, which is harsher than the one behind the published
columns:

- **Temporal is unaffected** and remains a lead of 14.8 points over the best
  published figure. Every claim built on it stands.
- **Open-domain becomes a lead**: 69.2 against a best published 51.15. The
  interval on 26 questions (50 to 84) still clears Zep and Mem0-graph and
  reaches Mem0, so on three conversations it is a strong lead, not yet a
  settled one.
- **Single-hop becomes a deficit**: 69.0 against 72.93 to 76.60.
- **Multi-hop becomes the largest deficit**: 53.8 against 61.70 to 67.13.
- The overall excluding-adversarial comparison is unaffected, because it does
  not depend on labels.

The standing rule holds: level with the leaders on the scalar, never ahead.
What changes is which categories carry the story. The honest per-category line
is now "ahead on temporal and open-domain inference, behind on multi-hop and
single-hop lookup", with the stricter judge and the sample stated.

## 6. Levers, ranked

"Capability" means the engine or reader genuinely gets better at memory.
"Reporting" means the number is described correctly. Nothing below is fitted
to a LoCoMo question: no lever is derived from a single failing item, and any
pack or skill change follows the standing rule that product-facing text is
authored walled off from the benchmark.

A measurement note governs every open-domain lever: the category is 26
questions on three conversations, one question is 3.8 points, and the
interval is 34 points wide. No open-domain lever can be evaluated on the
current sample. The staged ten-conversation, three-run configuration
(`config/locomo-next.json`) has 96 open-domain questions and is the first
setting in which one could be.

| # | Lever | Kind | Estimated effect | Effort | Risk to other categories or correctness |
|---|---|---|---|---|---|
| 1 | Correct the category alignment everywhere Table 1 is quoted, and state the mapping in the next run's report | Reporting | Open-domain moves from the only trailing category to a lead; single-hop and multi-hop are shown trailing | Low | None to correctness. It retires two "ahead" claims (single-hop, and multi-hop against Zep) that are currently published and misaligned |
| 2 | Single-hop: reader decline discrimination | Capability | 33 of the 58 single-hop failures are declines. The earlier commit experiment recovered 20 to 25% of declines under the strict judge; applied here, +5 to 8 questions, +3 to 4 points on single-hop | Medium | Adversarial (89.2%) can fall if declines are simply suppressed; must be measured on both |
| 3 | Multi-hop and synthesis: entity-scoped coverage for set and synthesis questions | Capability | 21 of 37 multi-hop failures had only partial evidence in context; open-domain q19, q20 and q51 share the shape. +3 to 6 multi-hop, +1 to 2 open-domain | Medium to high | More context raises adversarial over-answering risk, which was driven by topically adjacent context. Graph traversal was measured negative on multi-hop, so this must filter by entity rather than walk edges |
| 4 | Extraction of one speaker's assessments of another | Capability | 0 to 1 open-domain question; other effects unknown | Low to medium | Larger store and more confirm-band traffic |
| 5 | Recurring events as queryable dated occurrences | Capability | At most 1 open-domain question | Medium | Low. Partial dates now survive never-drop, which makes it possible. No reader-prompt instruction aimed at "how often" questions, which would fit a test item |

Not recommended, with the reason:

- **World-knowledge augmentation.** No open-domain failure needed knowledge the
  reader lacked, and the reader already uses general knowledge correctly.
- **Mem0-graph-style triplets or graph traversal for open-domain.** Mem0-graph
  scores below base Mem0 on this category, and Engraphy's own traversal was
  measured negative on multi-hop.
- **Reranking.** Measured and rejected earlier; the gold-bearing memory is
  usually already at rank 1.
- **Loosening the strict judge.** It causes four to five of the eight
  open-domain failures, but that effect is already reported openly as the
  reference-convention figure. Changing the strict rubric would remove the
  harder of the two published numbers.

## 7. Best honest reading

On the question as posed, the gap does not exist: correctly aligned, Engraphy's
open-domain result is the strongest of the four systems, subject to a 26-
question sample. The real work is in multi-hop and single-hop, where the
realigned table shows Engraphy behind, and where levers 2 and 3 are aimed.
Their estimated combined effect, if both land, is 3 to 5 points on single-hop
and 4 to 8 points on multi-hop under the strict judge, enough to close most of
the single-hop gap and about half the multi-hop gap. Those are estimates from
bucket sizes, to be confirmed on the ten-conversation run before any are
quoted.

## Sources

- Mem0 paper, arXiv:2504.19413, Table 1 (per-category J) and Table 2 (overall J), and its definitions of the categories and its answer prompt: https://arxiv.org/html/2504.19413v1
- Mem0 benchmark harness category names, `mem0ai/memory-benchmarks` at `4b61c5d`: https://raw.githubusercontent.com/mem0ai/memory-benchmarks/4b61c5d31b9c668a12b4f5e78064248a02c82d2b/benchmarks/locomo/prompts.py
- Zep / Graphiti paper, arXiv:2501.13956: https://arxiv.org/html/2501.13956
- Zep's rebuttal of Mem0's evaluation: https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/
- LoCoMo category IDs verified against question shape (evidence-turn counts per category): https://github.com/corbym/locomo-recordari
- Mem0 paper figures as reproduced by Memobase: https://github.com/memodb-io/memobase/blob/main/docs/experiments/locomo-benchmark/README.md
