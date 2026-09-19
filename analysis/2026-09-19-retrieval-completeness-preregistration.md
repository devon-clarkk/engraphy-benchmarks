# Retrieval completeness: decision rules, fixed before the reader measurement

Written 2026-09-19. The commit that adds this file precedes every reader or judge
call it governs.

Prototype: `devon-clarkk/engraphy` branch `feat/entity-complete-retrieval`,
commit `bdc6c17`, on main `299f5b3`. Store: the kept store of run
`locomo-definitive-20260917` (318 memories, conv-26, conv-30, conv-49).

## What was measured before this file

Only retrieval, with no LLM: `bench/completeness_recall.py` rebuilt every
question's retrieval against the kept store and counted the question's LoCoMo
evidence turns reaching context. Its k=20 arm reproduced 498 of the run's 500
saved envelopes id for id. The two limits (roster 100 titles, 10 source turns)
were fixed in code, with their reasons, before that measurement ran, and are not
changed by it or by anything below.

## The two additions

1. **Entity roster.** When a question names a person or thing in the store's own
   `person`/`thing` registry, add every other active memory whose title or body
   names it, by title and attributes only, most query-similar first, at most 100.
   Text filter only; no edge is followed.
2. **Source-turn backstop.** Add the 10 conversation turns ranked highest by the
   engine's hybrid arithmetic (cosine leg and lexical leg, 30 each, RRF k=60),
   skipping turns already quoted in a retrieved memory.

## Arms

All read every one of the run's 500 questions from saved envelopes, with the
definitive reader (`claude-opus-4-8`, stance `grounded`, contract `verify`, skill
`sha256:c3b00290...`), graded by the unchanged strict judge, one pass, with
`--reuse-verdicts` (an answer identical to the run's own takes the run's verdict).
Adversarial questions are graded by the abstention rule.

| Arm | Envelope |
|---|---|
| C0 | hybrid search, k=25: the staged run's configuration, and the control |
| A1 | C0 plus the entity roster |
| A2 | C0 plus the roster plus the source-turn backstop |

C0 is read fresh rather than taken from the run, so every comparison is between
two fresh reads that differ only in the envelope. C0 against the run's own
verdicts also measures the reader's replay churn.

## Decision rules

An addition is carried into the engine specification as shipping only if, against
C0, paired per question:

1. **Non-adversarial accuracy rises** with McNemar p < 0.05;
2. **adversarial accuracy does not fall** by more than 3 questions net, and any
   fall is not significant (McNemar p >= 0.05);
3. **no non-adversarial category loses** more than 3 questions net.

A1 is judged against C0; the backstop is judged as A2 against A1. An addition
that fails is reported with its numbers and specified as not shipping.

Reported regardless: recovery counts on the multi-hop and single-hop failure
classes (retrieval gap, extraction gap, evidence already complete), context size,
and the evidence coverage table.

## What is not done

No limit, threshold, render wording or entity rule changes after this file. No
question is excluded. The reader is not changed; whether the reader should answer
or decline is another workstream's lever and is held constant here.
