# Does the wider extraction prompt turn the store into a transcript?

Measured 2026-10-02 on the seen-split A/B stores, with no model in the loop:
`scripts/turn_verbatim.py`, output in
`results/locomo/locomo-extract-ab-20261002/turn-verbatim.json`.

## Why the question has to be asked

Storing turns is a design non-goal. The source-turn layer was measured on
2026-09-25 to cost 8 adversarial declines and was excluded for that and because
storing turns is not what the system is for. The wider extraction prompt stores
55% more memories, and `retain_source_text` appends the turns a memory cites to
its body verbatim, so a prompt that extracts more facts also drags more
transcript in behind them. A lever that reaches the excluded design by another
route should be caught before it ships, not after.

## What the stores hold

A turn counts as held when its first 60 normalised characters appear in some
memory of that scope, the same key the coverage tool uses against evidence turns.
1,297 turns across conv-26, conv-30 and conv-49.

| store | turns held verbatim | memories |
|---|---|---|
| `llm` (shipped) | 492/1,297 = 37.9% | 333 |
| `llm` (replicate) | 489/1,297 = 37.7% | 323 |
| `llm_wide` | 650/1,297 = 50.1% | 515 |

## Reading

The rise is 12.2 points, from 37.9% to 50.1%, and the replicate puts the
ingest-to-ingest floor on that comparison at 0.2 points.

Half the transcript is still not in the store. The excluded layer stored every
turn as its own retrievable row; this is the shipped `retain_source_text`
behaviour carrying cited turns along with more facts, and the shipped prompt
already holds 38% the same way. The wider prompt does not introduce a turn layer
and does not approach one: it moves an existing property from just over a third
to just over half.

The non-goal's stated cost did not materialise either. The source-turn layer was
excluded partly because it cost 8 adversarial declines, and more stored turn text
is more for an adversarial question to look true against. On this A/B the
adversarial rate is identical, 98 of 111 both ways, discordant 3 against 3,
p 1.0.

So the honest answer is: more of the conversation is in the store, by half as much
again, through a mechanism that already shipped, with no measured adversarial
cost and with the store still holding only half the turns. It is recorded here as
a number rather than settled as a principle, because where the line sits between
"a memory that quotes its source" and "a transcript" is the owner's call, not a
measurement's.
