# LoCoMo, run A: the consolidated result

> The consolidated figures for the current engine are the two-run means in
> `analysis/2026-10-09-locomo-two-run-consolidated-report.md`, and the
> publishable set is `WEBSITE-FIGURES.md`. This document records run A on its
> own.

One run of the current engine over the seven LoCoMo conversations that no lever
was tuned on. Two conventions, both reported. Every figure below recomputes from
files committed in this repository, and each table names the file it comes from
and the command that reproduces it.

- Engine: `aa7daa2b9c5f190ee3f10de5b9bf4cbaee44e5a6`, branch `bench/settle-20260930`
  of `devon-clarkk/engraphy`. The scoring path (`bench/core/run.py`) last changed
  at `af6c96e`; commits after it touch offline and reporting tools only.
- Artifacts: `results/locomo/locomo-settle-a/`
- Dataset: LoCoMo `locomo10.json`, sha256
  `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`, upstream
  commit `cbfbc1dba6bc53d00625212a0f22d55ffee7c1fc`. CC BY-NC 4.0, not
  redistributed here.
- Split: conv-41, conv-42, conv-43, conv-44, conv-47, conv-48, conv-50. 1,486
  questions, 1,151 non-adversarial, 335 adversarial, 209 sessions.

## Reproducing every number

    # strict and matched-convention tables, and the aligned standing
    python scripts/consolidate.py results/locomo/locomo-settle-a

    # the extraction lever, paired per question
    # arm_compare.py and extraction_gate.py live in the engine repository, at the
    # commit this run used
    git clone https://github.com/devon-clarkk/engraphy.git ../engraphy
    git -C ../engraphy checkout aa7daa2b9c5f190ee3f10de5b9bf4cbaee44e5a6
    python ../engraphy/scripts/arm_compare.py \
        results/locomo/locomo-settle-a/results.jsonl

`results/locomo/locomo-settle-a/REDACTIONS.md` lists what is committed and what
is withheld as dataset text, and `PROVENANCE.md` records the engine commit and branch, the dataset hash, the
models, the prompt hashes and the conventions of the matched pass.

## 1. The two conventions, and why both are here

**Strict** is Engraphy's own default and the harder of the two. The reader may
decline when memory does not support an answer; the judge requires every item of
a multi-item gold answer; each answer is graded best-of-3 to damp the judge's
measured per-pass instability; adversarial questions are included and scored.

**Matched convention** reproduces the conventions the published figures were
produced under, vendored verbatim from `mem0ai/memory-benchmarks` at
`4b61c5d31b9c668a12b4f5e78064248a02c82d2b`: an answer prompt that forces a
commitment rather than allowing a decline, a judge that accepts one item of a
multi-item gold answer with 14-day date and 50% duration tolerance, categories 1
to 4 only so adversarial is excluded, one judge pass, and up to 200 memories in
context. Engraphy's engine returns at most 25 results by design, so it competes
under that convention with a smaller context than the convention permits.

The published figures are matched-convention figures. The matched-convention
table is therefore the like-for-like comparison, and the strict table is the
conservative number Engraphy reports as its own default.

Models, both conventions: extractor, reader and adjudicator `claude-opus-4-8`;
judge `claude-sonnet-5`, reached through the Claude Code CLI. Embedder
`nomic-ai/nomic-embed-text-v1.5` at revision
`e9b6763023c676ca8431644204f50c2b100d9aab`, onnx-fp32, 384 dims. Recorded in
`results/locomo/locomo-settle-a/manifest.json` and `reference/manifest.json`.

Note on comparability of answerer models: Mem0's published 66.88 used a
GPT-4o-mini answerer and is the mean of 10 runs. Engraphy's figures use the
models above. A reader model is part of a memory system's measured result under
both conventions, and neither side's figure isolates retrieval from reading. This
is a difference in setup that no amount of convention matching removes, and it is
stated rather than papered over.

## 2. The corrected category alignment

The Mem0 paper's per-category table (arXiv:2504.19413, Table 2) carries column
headers that do not name the LoCoMo categories they hold. Of the 24 possible
assignments of its four columns to LoCoMo's four non-adversarial categories,
exactly one reproduces the paper's own published overall for all five systems it
reports, to within 0.01:

| paper column | LoCoMo category |
|---|---|
| "Single-Hop" | category 1, multi-hop |
| "Multi-Hop" | category 3, open-domain |
| "Open-Domain" | category 4, single-hop |
| "Temporal" | category 2, temporal |

Derivation and sources: `analysis/2026-09-19-locomo-open-domain-findings.md`, and
the Fable analysis node `d7c05bc3`. Every per-category comparison below uses this
alignment; `scripts/consolidate.py` holds the remapped published values, so the
alignment is applied by code rather than by hand.

## 3. Strict convention: Engraphy's own default

From `results/locomo/locomo-settle-a/results.jsonl`, arm
`llm_wide-conversational/search_only/always_distinct/k25`.

| | Engraphy (strict) | Mem0 | Mem0-graph | Zep (as Mem0 measured) | Zep (self-reported) |
|---|---|---|---|---|---|
| excluding adversarial | **74.8%** (861/1,151) | 66.88 | 68.44 | 65.99 | 75.14 +/- 0.17 |
| single-hop | 83.0% (543/654) | 72.93 | 75.71 | 76.60 | |
| multi-hop | 55.9% (113/202) | 67.13 | 65.71 | 61.70 | |
| temporal | 74.7% (168/225) | 55.51 | 58.13 | 49.31 | |
| open-domain | 52.9% (37/70) | 51.15 | 47.19 | 41.35 | |
| all categories | 78.2% (1,162/1,486) | | | | |
| adversarial | 89.9% (301/335) | not reported by any of the three | | | |

Read honestly, under the strict convention:

- Overall it is **level with Zep's own self-reported figure** (74.8% against
  75.14%) and above the figures Mem0 published for Mem0, Mem0-graph and Zep.
- **Multi-hop is behind all three** and is the real deficit, not a rounding
  artefact.
- Temporal is far ahead, by 16.5 to 25.4 points.
- This table is not like-for-like: it puts Engraphy's harder convention against
  figures produced under the permissive one. It is included because it is the
  number Engraphy stands behind as its default, and because publishing only the
  favourable convention would be the thing a sceptic should attack.

## 4. Matched convention: the like-for-like comparison

From `results/locomo/locomo-settle-a/reference/results.jsonl`, 1,151
non-adversarial questions, one judge pass, conventions as vendored above.

| | Engraphy (matched) | Mem0 | Mem0-graph | Zep (as Mem0 measured) | Zep (self-reported) | margin over the best of them |
|---|---|---|---|---|---|---|
| excluding adversarial | **91.0%** (1,047/1,151), Wilson 95% [89.2, 92.5] | 66.88 | 68.44 | 65.99 | 75.14 +/- 0.17 | +15.8 |
| single-hop | 92.7% (606/654) | 72.93 | 75.71 | 76.60 | | +16.1 |
| multi-hop | 93.6% (189/202) | 67.13 | 65.71 | 61.70 | | +26.5 |
| temporal | 90.7% (204/225) | 55.51 | 58.13 | 49.31 | | +32.6 |
| open-domain | 68.6% (48/70) | 51.15 | 47.19 | 41.35 | | +17.5 |

Engraphy is the highest figure in every category, including multi-hop.

**Why multi-hop moves from 55.9% strict to 93.6% matched.** This is the largest
convention effect in the table and a sceptic will find it, so it is explained
here. Multi-hop gold answers are typically multi-item. The strict judge requires
every item; the matched judge accepts one. The same stored memory and the same
retrieved context therefore score very differently, and the gap is a property of
the grading rule rather than of the retrieval. The honest reading is that under
the convention the published figures use, Engraphy answers multi-hop questions at
least as completely as the leaders do, and under its own stricter rule it does
not yet answer them completely.

**What else the matched convention buys.** Measured earlier on the seen split
with two controls, in `results/locomo/locomo-definitive-20260917/reference/`:
Engraphy's strict judge re-graded all 346 accepted matched-convention answers
(control A), and 60 deliberately mismatched answers were graded by both judges
(control B), where the matched judge accepted 6 of 60 against the strict judge's
1 of 60. On that split a confabulation adjustment removed 11 credits where only
the matched rules accepted and no evidence turn had been retrieved, giving a
defensible 86.1% against a raw 88.95%, a floor of 75.6% and a ceiling of 88.9%.
**Those controls were run on the seen split at width 20 and have not been rerun
for run A**, so the 91.0% here is the raw matched-convention figure. The controls
are cited to size the effect, roughly 3 points of adjustment and a wide floor,
not to adjust this number. Running them for run A is the single cheapest thing
that would harden this figure further.

## 5. The extraction lever, measured out of sample

Run A carries two arms on one ingest, so the wider extraction prompt is compared
against the shipped one on the same conversations, same reader, same judge,
paired per question. From `arm-compare.json`, reproducible with `arm_compare.py`.

| | shipped prompt | wider prompt | paired result |
|---|---|---|---|
| non-adversarial | 72.11% (830/1,151) | 74.80% (861/1,151) | discordant 62/93, exact McNemar **p 0.016** |
| adversarial | 88.96% (298/335) | 89.85% (301/335) | discordant 11/14, p 0.69 |
| single-hop | 78.90% | 83.03% | +4.13 |
| multi-hop | 55.45% | 55.94% | +0.49 |
| temporal | 73.78% | 74.67% | +0.89 |
| open-domain | 51.43% | 52.86% | +1.43 |

**+2.69 points out of sample**, against +7.46 points on the seen split the prompt
was fitted to. The in-sample figure is validation, not effect. The gain is
concentrated in single-hop, which is what the mechanism predicts: single-hop is
one fact in one turn, and what the wider prompt contributes is storing facts the
shipped prompt discarded. Multi-hop barely moves, consistent with multi-hop being
limited by retrieval and reasoning rather than by what is stored.

Discordance is high relative to the net: 155 questions change verdict to produce
a net 31. The effect is significant against chance at p 0.016. It has **not** been
checked against run-to-run variation, because that needs a second run.

**Disclosure.** The wider prompt was written against
`2026-09-30-extraction-gap-labels.json`, 46 questions all on the seen split,
hand-labelled by reading each question's gold answer and its cited evidence
turns. The prompt contains no question, gold answer or conversation text, so what
was fitted is the kind of fact worth storing; the exposure is real and bounded,
and the held-out split was never read or labelled while the prompt was written.
The gap-set recovery figure (9 of 46 to 28 of 46) is circular and is not cited as
evidence. Full disclosure in
`analysis/2026-09-30-settling-run-preregistration.md`.

## 6. Retrieval isolation, measured with no model in the loop

From `results/locomo/locomo-settle-a/retrieval-isolation.txt`, built from run A's
own store. "Recall" is the share of cited evidence turns present in the retrieved
context; "all evidence" is the share of questions whose every evidence turn is
present. No reader and no judge are involved, so these are retrieval properties
and not accuracy.

| retrieval arm | evidence recall | all evidence held | context size |
|---|---|---|---|
| k=20 | 86.47% | 81.88% | 12,034 chars |
| **k=25 (shipped)** | **87.49%** | **83.10%** | 15,029 |
| k=25 + entity roster | 92.62% | 89.11% | 25,807 |
| k=25 + source turns (excluded by design) | 91.29% | 87.37% | 16,701 |
| k=25 + both | 95.97% | 93.38% | 27,489 |
| flat 50 | 88.86% | 84.32% | 18,028 |
| entity 50 | 90.13% | 86.06% | 29,693 |

Width 25 over width 20 is +1.02 points of recall for 25% more context. The entity
roster is +5.13 points of recall over the shipped arm for 72% more context.

**The accuracy-level replays of k=20 and roster-on were not run**, by decision, to
avoid roughly 10,000 further model calls. So the rows above are retrieval
measurements only. What is known about whether that recall converts: on the seen
split the roster replay gained 5 non-adversarial questions at p 0.46 with no
adversarial cost, which did not meet the bar to ship, and the roster stays
default-off. The source-turn layer is excluded on design grounds and because it
was measured to cost 8 adversarial declines.

## 7. What a single run does and does not support

The 95% Wilson intervals above cover **sampling** error: the chance that these
1,151 or 1,486 questions happened to favour the system. They do not cover
**run-to-run** variation, which comes from extraction being a model call, so a
fresh ingest of the same conversations writes a slightly different store.

What is known about the size of that second component, from the stage-1 replicate
in `results/locomo/locomo-extract-ab-20261002`: two ingests of the same prompt on
the same conversations differed by 0.8 points of store coverage, by 0.2 points of
verbatim turn share, and by 10 memories in 333. That is a small number, but it is
a measure of store variation, not of accuracy variation, and accuracy variation
has not been measured on this split. A second run (run B) is the only thing that
measures it.

### Fully defensible on this single run

- Every exact figure in sections 3, 4, 5 and 6, quoted as the result of one named
  run over a named split with the artifact path attached.
- Under the matched convention, **leading every LoCoMo category**. The smallest
  margin is +15.8 points overall against Zep's own self-reported figure, and
  +16.1 points in the closest category. The lower bound of Engraphy's 95%
  interval, 89.2%, is 14 points above the highest competitor figure including its
  stated error. No plausible run-to-run variation of a few points closes a gap of
  that size.
- Under the strict convention: ahead of the published Mem0, Mem0-graph and Zep
  figures overall, **level with Zep's self-reported 75.14%**, and behind all three
  on multi-hop.
- The extraction lever helps out of sample, +2.69 points at p 0.016.

### Needs run B before it can be said without the single-run hedge

- Any figure stated as a typical, average or expected value, or carrying a
  plus-or-minus: "averages 91%", "91.0% +/- x", "consistently above 90%". One run
  has no spread, and `consolidate.py` prints "one run, no spread" for exactly this
  reason.
- Any comparison whose margin is within a few points, which on these tables means
  the strict overall figure against Zep's self-reported 75.14%, a 0.34-point gap.
  On one run that is level, and no wording should make it a lead.
- Reproducibility and stability claims: "repeatable", "stable across runs",
  "robust".
- The extraction lever's +2.69 as an effect that clears run-to-run variation. It
  clears chance; the pre-registered rule also asks it to clear the spread between
  runs, and that spread does not exist yet.

## 8. Caveats that travel with every figure

1. **One run.** Reported as such everywhere, with sampling intervals given and
   run-to-run spread unmeasured.
2. **Held-out split, seven of ten conversations.** The other three carried the
   tuning and are reported separately. Figures on the ten-conversation whole suite
   do not exist for this engine.
3. **Answerer models differ from the published setups.** Engraphy's figures use
   `claude-opus-4-8` to read and `claude-sonnet-5` to judge; Mem0's 66.88 used
   GPT-4o-mini as the answerer and is a mean of 10 runs.
4. **The matched-convention figure is raw.** The confabulation controls that
   bounded the earlier seen-split figure have not been rerun for run A.
5. **Zep's figure is disputed.** Mem0 published 65.99 for Zep; Zep self-reports
   75.14 +/- 0.17 after what it describes as three implementation errors in that
   evaluation. The higher of the two is used as the comparator throughout.
6. **Mem0's own 92.5%** (mem0.ai/research) states no retrieval budget, no answerer
   or judge model, no judge prompt and no run count, so it is not used as a
   comparator. Other vendor figures in the 90s found by search are self-reported
   with no stated methodology and are likewise not used.
7. **Multi-hop under the strict convention is a genuine deficit**, and the
   strict-to-matched gap there is a grading-rule effect, explained in section 4.
8. **Engraphy competes under the matched convention with at most 25 memories in
   context** where the convention permits 200.
