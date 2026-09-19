# Levers 2, 3 and 4: decision rules, fixed before measurement

Written 2026-09-16, before any sweep, replay or run under these changes produced
a number. The commit that adds this file precedes every measurement it governs.

Engine under test: `devon-clarkk/engraphy` branch
`bench/locomo-conventions-reader-width`, stacked on
`feat/flexible-dates-never-drop` (PR #23, head `99b38a5` at the time of writing).

## Lever 4: retrieval width

**Instrument.** `bench/k_sweep.py`, over the extracted store of run
`fullrun-conv-20260916`. Evidence recall at width k is the share of a question's
LoCoMo evidence turns quoted verbatim by at least one of the k returned memories.
No reader and no judge take part, so the width is not chosen against the score.

**Widths measured.** 10, 15, 20, 25, 30, 40, 50.

**Rule.** The chosen width is the smallest measured k whose evidence recall over
all non-adversarial questions is within 1.0 percentage point of the recall at
k=50. If that is 10, the width stays at 10.

**Effect on the final number.** Measured by replaying the lever 3 reader on the
saved envelopes at k=10 and at the chosen k, and again in the definitive run. The
replay does not move the choice, with one exception fixed here: if strict
non-adversarial accuracy at the chosen k is lower than at k=10 by more than the
reader's own replay churn, the width stays at 10.

## Lever 3: reader abstention discrimination

**Change.** One design, fixed before measurement: a section in
`skills/answer-discipline.md` requiring a returned memory to match the subject and
the occasion a question asks about before the reader answers from it or declines
for want of it, and a `verify` reply contract that puts that check on a CHECK line
before the ANSWER line. Only the answer is graded.

**Instrument.** `bench/replay.py`, re-reading the saved k=10 envelopes of
`fullrun-conv-20260916` with the new reader, and with the previous reader (old
skill, `direct` contract) on the same envelopes as the baseline. Both are graded
by the unchanged strict judge.

**Validation order.** First the 76 non-adversarial questions the run declined and
the 111 adversarial questions, then the answered non-adversarial questions.

**Success requires all three:**

1. strict non-adversarial accuracy rises against the baseline replay;
2. adversarial accuracy (correct declines) does not fall against the baseline replay;
3. non-adversarial answers the baseline gets right do not regress by more than the
   baseline replay's own churn against the original run.

**Revisions.** At most one revision of the wording, disclosed with both
measurements, and only in response to a failure of criterion 2 or 3.

## Lever 2: matched conventions

No tuning takes place. The reference prompts are vendored verbatim from
`mem0ai/memory-benchmarks` at `4b61c5d`, and every place the reproduction differs
from the reference is recorded in the manifest. The strict number stays the
primary figure.

## Reporting

A single run cannot attribute a 2 point move to one lever: per-question churn
between two runs of one configuration was 19.6% on 2026-09-16. Levers 3 and 4 are
reported combined against the never-drop baseline run, with each lever's replay
effect stated beside its measured churn.

## Addendum, 2026-09-19: width for the next run

The rule above selected k=20 for `locomo-definitive-20260917`, because evidence recall
at 20 (68.3%) was within 1.0 point of the recall at the cap (69.2% at 25). For the next
run the width is set to 25, the engine's result cap, by the owner's decision. It is
recorded as a decision, not as the rule's output, and the figures measured at k=20 stay
as published. The next run's configuration is staged in `config/locomo-next.json`.
