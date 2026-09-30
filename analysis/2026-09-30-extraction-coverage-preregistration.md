# Extraction coverage: decision rules, fixed before measurement

Written 2026-09-30. The commit that adds this file precedes every ingest it
governs.

Prototype: `devon-clarkk/engraphy` branch `feat/extraction-coverage`, a change to
`bench/prompts/extract.md` only. No engine file changes.

## The problem being attacked

On run `locomo-definitive-20260917`, 34 of 58 single-hop failures and 12 of 37
multi-hop failures have evidence that no stored memory quotes. The store holds
318 memories from 1,297 turns, 0.25 per turn, while the write path refused only
14 and dedup merged 1. The loss is at drafting, not at writing.

Hand-labelling all 46 (`runs/extraction/labels.json` on
`feat/entity-complete-retrieval`) gives: 11 interpersonal acts (advice, offer,
request), 7 assessments of another person, 5 stated reactions, 8 incidental
concrete details, 12 dropped members of a recurring set, 3 ambiguous.

## The change

Three edits to the extraction prompt, each general and each naming no benchmark,
category or question shape:

1. The instruction to "prefer fewer, well-formed memories over many fragments" is
   replaced by a completeness instruction.
2. The exclusion of "anything whose meaning depends entirely on the immediate
   exchange" is replaced by an explicit inclusion of what one person says to or
   about another, recorded with speaker and addressee named.
3. The prior-titles rule gains: a new instance of a recurring thing is a new
   fact, not a restatement.

## Arms

Same engine, same pack, same models, same dedup policy; the extraction prompt is
the only difference. Each arm ingests into its own fresh space.

| Arm | Prompt |
|---|---|
| BASE | `extract.md` as shipped |
| WIDE | `extract.md` with the three edits |

Ingest only, no reader and no judge, on conv-26, conv-30 and conv-49: the same
conversations the failure set comes from.

## Primary measure

**Gap-set coverage.** Of the 46 extraction-gap questions, the share whose cited
evidence turns are quoted by at least one stored memory, measured exactly as
`bench.k_sweep.recall` measures it (first 60 normalised characters of the turn,
found in a memory body). BASE is near zero by construction; WIDE is the number
that matters.

## Guards, all reported whether or not they pass

1. **Store growth.** Drafts per turn and memories written. A store more than
   three times the size of BASE is a bloat failure, reported as such.
2. **Overall evidence recall.** Retrieval at k=25 over all non-adversarial
   questions, `bench.completeness_recall`. Must not fall against BASE: more
   memories must not crowd out the ones that were already found.
3. **Duplicate pressure.** Confirm-band rate and merged counts, to show whether
   the extra memories are genuinely distinct or restatements.

## Decision rule

The change is carried forward only if gap-set coverage reaches at least 40% of
the 46 **and** overall evidence recall does not fall **and** store growth stays
within three times BASE.

Meeting that rule does **not** mean it ships. Coverage is not accuracy, and more
memories about a named person is exactly the condition that inflated adversarial
over-answering in the retrieval-completeness work (2026-09-25). A reader and
judge pass over both arms, including all 111 adversarial questions, is required
before any ship decision, and it is specified here rather than left to
judgement: adversarial must not fall by more than 3 net.

## What is not done

No prompt revision after seeing any measurement below. If the first wording
fails, that is the result. No question is inspected to choose wording: the three
edits were written from the category counts and from how the reference systems
extract, both of which are recorded above.
