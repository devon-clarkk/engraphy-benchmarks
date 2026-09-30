# Extraction misses: what the store never learns, and why

Date: 2026-09-30. Run analysed: `locomo-definitive-20260917`.
Decision rules fixed first: `analysis/2026-09-30-extraction-coverage-preregistration.md`.
Prototype branch: `devon-clarkk/engraphy` `feat/extraction-coverage`. Not merged.

**Status: characterisation and root cause are complete and measured. The
prototype is written but its measurement is blocked by the usage cap.** Section 7
says exactly where it stopped and how to resume.

## 1. The size of the hole

The store holds 318 memories drawn from 1,297 turns, 0.25 per turn. Of the
failures on the definitive run, 34 of 58 single-hop and 12 of 37 multi-hop have
evidence that no stored memory quotes: 46 questions, 11.8% of the
non-adversarial set, that no read-path change can reach.

This is drafting loss, not write loss. Across the three conversations the write
path refused 14 writes, dedup merged 1, and the confirm band resolved 197 of 197
to insert. Essentially everything the extractor proposed was stored; the
extractor proposed a quarter of a memory per turn.

## 2. What kind of facts are missed

All 46 hand-labelled from their gold answer and cited evidence turns
(`2026-09-30-extraction-gap-labels.json`).

| Category | n | Share | Example |
|---|---|---|---|
| Interpersonal act: advice, suggestion, offer, request | 11 | 24% | "maybe you should check out a dream interpretation book" |
| Assessment of the other person, their work or decision | 7 | 15% | "the studio looks amazing"; "you'll be an awesome mom" |
| Stated emotion or reaction | 5 | 11% | "I'm excited"; "they were scared but we reassured them" |
| Incidental concrete detail or one-off anecdote | 8 | 17% | the dog hid his bone in a slipper; a rainbow sidewalk; a trophy |
| Dropped member of a recurring set | 12 | 26% | camping at the beach, when a camping memory already exists |
| Ambiguous evidence | 3 | 7% | the cited turn does not carry the gold |

The two failure shapes separate cleanly. **Single-hop misses are conversational**:
things said in the exchange, mostly by one speaker about or to the other, plus
small physical particulars. **Multi-hop misses are set members**: the store keeps
one instance of a recurring activity and drops the rest, so a question asking for
all of them cannot be answered however well retrieval works.

## 3. Root cause: three clauses of the extraction prompt

`bench/prompts/extract.md`, on the engine commit the definitive run used. Each
clause maps onto a category above.

1. **"Prefer fewer, well-formed memories over many fragments."** A direct
   instruction to suppress volume, and the likeliest source of the 0.25 per turn
   rate.
2. **"Do not extract ... anything whose meaning depends entirely on the immediate
   exchange."** Advice, assessments and reactions are exactly that. This clause
   covers categories A, B and C: 23 of the 34 single-hop misses.
3. **"Do not extract a fact that is already covered by one of the prior titles
   unless this window genuinely changes or extends it."** A second camping trip
   reads as covered by the first. This is category E, and it is why multi-hop set
   questions fail.

Two things are **not** the cause, which matters because they were the obvious
suspects:

- **Not the typed-attribute constraints.** The pack's `fact` and `opinion` types
  accept all of these; `attrs` are optional on both (`packs/conversational/pack.yaml`).
  Nothing about an assessment or a piece of advice is unrepresentable.
- **Not dedup or the write band.** Merged 1, confirm band all resolved to insert,
  14 refusals total (`runs/.../ingest.jsonl`).

The extraction window is a contributing factor: `bench/core/extract.py` windows
up to 40 turns (`max_turns: int = 40`), so a typical 20-turn session is one call
producing about five memories for the whole session.

## 4. How the leaders extract more

- **Graphiti (Zep)** extracts **per message**. Its edge-extraction prompt says
  "Extract all factual relationships between the given ENTITIES based on the
  CURRENT MESSAGE", and requires the fact to "preserve all specific details from
  the source text: proper nouns, brand names, product names, model numbers,
  quantities, counts, colors, materials, physical descriptions, specific items,
  named locations, and named activities". Episodes are also kept losslessly
  beneath the entity graph, so nothing said is unrecoverable.
- **Mem0** extracts per message pair across seven declared content categories
  (preferences, personal details, plans, service preferences, health,
  professional details, miscellaneous), then reconciles at fact level with
  ADD / UPDATE / DELETE / NOOP.

The shared pattern: **extract per message, be inclusive, reconcile duplicates
afterwards.** Engraphy extracts per 40-turn window, asks for parsimony up front,
and reconciles nothing afterwards, so a fact declined at drafting is gone for
good. That single ordering difference explains the drafting rate and all three
prompt clauses above.

## 5. The change under test

Three edits to `bench/prompts/extract.md`, general, naming no benchmark,
category or question shape (commit `ef8ae9f`, prompt sha256 `2f3fa4c9e6c1a457`):

1. Parsimony replaced by completeness: "A window that supports twelve distinct
   facts should produce twelve memories, not three that gesture at them."
2. The immediate-exchange exclusion replaced by an explicit inclusion: what one
   person says to or about another is a fact about them, **recorded with the
   speaker and the person addressed both named**.
3. The prior-titles rule gains: a new instance of a recurring thing, on another
   occasion or in another place or with another object, is a new fact.

Edit 2 names the attribution deliberately. The retrieval-completeness work
(2026-09-25) showed that adding raw conversation turns gained 21 non-adversarial
questions and lost 8 adversarial declines, because the lost questions were
misattribution traps and a raw turn carries words without saying whose statement
it is. An attributed memory ("Evan suggested Sam try painting to de-stress") is
the same content with the attribution restored, so the same content may be
storable without the same cost. That is the hypothesis this prototype tests, and
it is a hypothesis, not a result.

## 6. Estimated recovery, and the risks

**Estimate, not a measurement.** The 46 questions are 11.8 points of the
non-adversarial set and are the ceiling. Coverage is not correctness: when the
source-turn experiment put this same evidence in front of the reader, 18 of 34
single-hop extraction gaps converted to correct answers, about 53%. Applying a
similar conversion to 46 gives roughly **+4 to +7 points excluding adversarial**,
contingent on the reader, and entirely unmeasured until section 7 runs.

Three risks, all to be measured rather than argued:

1. **Adversarial inflation.** More memories about a named person is the exact
   condition that cost 8 adversarial declines before. Attribution is the
   mitigation and may not be enough. The pre-registration requires a reader pass
   over all 111 adversarial questions before any ship decision.
2. **Store bloat and duplicate pressure.** A 2x to 3x larger store raises
   confirm-band traffic, which is a real per-write cost for a deployment, and
   risks crowding good memories out of a fixed-width retrieval.
3. **Extractor cost.** More output tokens per window, and the same again on
   every future ingest.

## 7. Where the measurement stopped

The WIDE ingest was launched over conv-26, conv-30 and conv-49 and **produced
nothing**, because the account hit the usage cap at the first extractor call.
Resume by rerunning `runs/ingest_wide.sh` on the branch (run id `extract-wide-a`,
into its own space on the `engraphy-levers-pg` store; the definitive space is
untouched and still holds its 318 memories). Then:

1. `bench.completeness_recall` for gap-set coverage and overall evidence recall;
2. a reader and judge pass over both arms including all 111 adversarial questions.

### A harness defect found by this, and fixed

The capped run did not fail. It logged "0 drafts to 0 nodes" for each
conversation and exited 0 with `done: true`. `QuotaExhausted` subclasses
`LLMError`, and `LLMExtractor.extract` caught `LLMError` broadly and returned an
empty window, so a usage stop was recorded as "this window contributed nothing"
for every window in the run.

Any capped ingest therefore silently produced an empty store and marked itself
complete. Fixed on the branch (commit `3cf6699`, three tests): `QuotaExhausted`
now propagates to the run loop, which checkpoints and resumes it. This is worth
carrying to the staged ten-conversation run independently of anything else here,
because that run ingests over three passes and would have been vulnerable to
exactly this.

## 8. Recommendation, ranked

| # | Action | Estimated gain | Effort | Risk |
|---|---|---|---|---|
| 1 | Port the quota fix (`3cf6699`) before the next multi-run ingest | none directly; prevents a silently empty run | trivial | none |
| 2 | Measure the WIDE prompt as specified in the preregistration | +4 to +7 pp excl. adversarial, unmeasured | one ingest plus one reader pass | adversarial inflation, store bloat |
| 3 | If WIDE passes, re-measure on held-out conversations before shipping | confirms the number is not fitted | one ingest | low |
| 4 | Consider per-message extraction, as both leaders do | unquantified, likely larger than the prompt change | large: changes ingest cost model | cost per ingest, duplicate pressure |

Lever 2 is the cheap test and should run first. Lever 4 is the structural
version of the same finding and should not be attempted until the prompt change
has been measured, since it is the same hypothesis at ten times the cost.
