# The reader's answer-versus-decline decision: signals, a tuned decision, and its frontier

Date: 2026-09-19. Scope: only the decision the reader makes from the memory it was
handed. Retrieval completeness is a separate line of work. Source: run
`locomo-definitive-20260917` (engine 3df1a4d, k=20, strict judge), its saved envelopes,
answers and the reader's CHECK lines. Nothing here reran the pipeline. Question text is
withheld as in the rest of this repository; questions are named by id.

Engine branch: `bench/reader-decline-audit` (commit a620a78, on PR #27 head 416234c),
not merged and not pushed.

## 1. The finding that reframes the task

The run declined 144 questions: 99 adversarial (all correct) and 45 non-adversarial (all
scored wrong). Of the 45, 33 are single-hop, 9 temporal and 3 multi-hop.

The 33 single-hop declines are not 33 answerable questions. Each one was read against
the memory the reader was handed:

| what the retrieved memory holds | single-hop | all 45 | can the reader fix it? |
|---|---:|---:|---|
| **Absent.** The asked fact is not in the 20 returned memories for the right subject. | 20 | 27 | No. The decline is correct. This is extraction or retrieval. |
| **Other owner, or contradicted.** Memory holds the fact for the other speaker, in the reverse direction, or about a different object. | 6 | 9 | Not without giving up the adversarial score (see below). |
| **Unrecorded detail.** One memory fits the subject and event and states the fact; the question adds a date, a description or a framing phrase memory does not keep. | 7 | 9 | Yes. This is the whole reader-side headroom. |

So the reader-side ceiling is 7 single-hop questions (9 across categories), not 33. 20 of
the 33 belong to the retrieval and extraction work.

The middle row is structurally identical to LoCoMo's adversarial traps, which are built by
taking a real fact and naming the other speaker. In three cases the dataset holds both
sides of the same fact with opposite expectations:

| expects an answer | expects a decline | same fact |
|---|---|---|
| conv-26:q94 | conv-26:q161 | memory records it for the subject of q161; the run answered q161 with the gold text and was scored wrong, and declined q94 and was scored wrong |
| conv-49:q152 | conv-49:q194 | same pattern |
| conv-30:q67 | conv-30:q100 | the same altered object in both |

No decision rule can score both sides of such a pair. They bound the joint score and should
be reported as label noise, not chased.

## 2. Signals, and how well each separates a good decline from a bad one

Good decline = adversarial, declined (99). Bad decline = non-adversarial, declined (45; 33
single-hop). AUC is the probability the signal ranks a bad decline above a good one; 0.5 is
no information.

| signal | good declines | bad declines (single-hop) | AUC | verdict |
|---|---:|---:|---:|---|
| top similarity | 0.742 | 0.758 | 0.65 | weak |
| mean similarity, top 3 | 0.716 | 0.745 | 0.69 | weak; a floor cannot separate them |
| similarity gap, rank 1 to 5 | 0.054 | 0.039 | 0.41 | none |
| share of the question's content words found in the best memory | 0.669 | 0.428 | **0.27** | inverted |
| the same, restricted to memories titled with the question's subject | 0.348 | 0.382 | 0.56 | weak |
| count of memories covering half the question's words | 2.5 | 1.6 | 0.36 | inverted |
| **swap gap**: best coverage anywhere minus best coverage under the subject | 0.321 | 0.045 | **0.76** (good above bad) | useful |
| question asks "when" | 0% | 0% (22% of all 45) | | adversarial has no "when" questions |
| question carries a calendar date | 6% | 18% | | weak alone |
| **the reader's own decline reason names another owner** | 70 of 99 | 6 of 33 (8 of 45) | | strong |

Three things follow.

- **Similarity does not discriminate.** This reproduces the 2026-09-16 result on a new run:
  over-answered adversarial questions have higher top similarity (0.784) than correctly
  declined ones (0.742).
- **Word overlap is inverted.** "The entity and the attribute appear in the context" is
  more true of a trap than of a wrongly declined lookup, because a trap copies a real
  fact's wording and most wrongly declined lookups have no supporting memory at all.
  Overlap only becomes useful as the swap gap: wording present in memory but not under the
  question's subject.
- **The discriminating signal is the kind of mismatch, not its size.** A good decline is
  "another owner" (70 of 99) or "contradicted or absent" (29). A recoverable decline is
  "one memory fits; the question adds a detail memory never kept". That is a judgment about
  content, which is why the tuned decision below is a reader step and not a score threshold.

## 3. The tuned decision: audit a decline by kind

`skills/decline-audit.md` on the branch. After the first call declines, a second call sorts
the decline into other-owner, contradicted, absent or unrecorded-detail. Only
unrecorded-detail turns it into an answer, under four tests: exact subject, the detail is
incidental to the asked fact, one memory fits, that memory states the fact. A "when"
question takes any time anchor memory keeps. The rule is stated in terms of what memory
records, names no dataset and no category, and the hard invariant is unchanged.

Two properties matter for measurement:

- The first call is byte for byte the published reader (same system hash), and a question
  it answered is never touched. So the 12 adversarial over-answers and all 344 answered
  questions cannot move, and the effect is fully measured on the 144 saved declines.
- It is off by default (`--reader-audit on`), and `bench.replay --audit-source-declines`
  measures it on any completed run at one call per decline.

## 4. The frontier, measured on the saved 144 declines

Strict judge, best of 3, on every decline the audit turned into an answer. Baseline:
adversarial 99/111 = 89.2%, single-hop 129/187 = 69.0%, non-adversarial 260/389 = 66.8%.

| operating point | declines overturned | single-hop recovered | other recovered | new wrong answers | adversarial lost | adversarial | single-hop | non-adversarial |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| audit off (published) | 0 | 0 | 0 | 0 | 0 | 89.2 | 69.0 | 66.8 |
| audit, sees the first-pass reason, high confidence only | 0 | 0 | 0 | 0 | 0 | 89.2 | 69.0 | 66.8 |
| **audit, sees the first-pass reason** | 5 | 1 | 1 temporal | 3 | **0** | **89.2** | 69.5 | 67.4 |
| blind audit, swap gap at most 0.25 | 6 | 1 | 1 temporal | 4 | 0 | 89.2 | 69.5 | 67.4 |
| blind audit, no gate | 9 | 1 | 1 temporal | 5 | 2 | 87.4 | 69.5 | 67.4 |
| hand-review ceiling for any reader-side rule | 9 | 7 | 2 | 0 | 0 | 89.2 | 72.7 | 69.2 |
| answer every decline | 144 | at most 13 | at most 5 | at least 27 | 99 | 0.0 | | |

Recovered by every audit variant: conv-26:q137 and conv-30:q21. "New wrong answers" are
declines that became wrong answers; they do not change the score, since a decline was
already scored wrong, but they are worse for a user than a decline.

The curve is short and flat. Holding adversarial at 89.2% is achievable (the informed audit
lost none of 99), but what it buys is 1 single-hop question and 1 temporal, 0.5 points on
non-adversarial, inside single-run noise. Pushing further (the blind audit) buys nothing
more and starts losing adversarial declines. The reader reaffirms its own reading on 5 of
the 9 hand-labelled recoverable questions even under an explicit rule, and 3 of the 5 it
did overturn were wrong.

## 5. Recommendation

1. **Operating point: the informed audit, off by default.** It is the only point that
   recovers anything at zero measured adversarial cost. Its expected gain is about half a
   point, so it is not worth a separate arm in the staged run.
2. **How it composes with the retrieval change and the staged k=25 run.** Because the audit
   only acts on first-pass declines, it does not need its own runs. After each of the three
   staged runs, replay that run's declines with `--audit-source-declines` (about 29% of
   questions, one call each, plus judge calls on the few overturned). That gives the audit's
   effect on all ten conversations, seven of them unseen here, which is the held-out test
   this analysis could not run. Report it as a disclosed secondary figure.
3. **Where the single-hop points are.** 20 of the 33 declines have no supporting memory in
   the top 20. Recall at k=25 and the extraction gaps behind the "absent" rows decide
   single-hop, not the reader's willingness to answer. The ids in the absent row are in the
   appendix for the retrieval work.
4. **Do not loosen the subject check.** 70 of the 99 correct adversarial declines rest on
   it, and the 6 single-hop declines it costs are the mirror images of adversarial traps.

Limits: one run, three conversations, a stochastic reader; the hand review and the audit
rule were written by someone who had read these declines, which is why the rule is stated
generally and why the unseen conversations of the staged run are the real test. The swap
gap threshold 0.25 was fixed before the blind run was scored and was not tuned.

## Appendix: hand review of the 45 non-adversarial declines

- Absent (27): conv-26 q125 q128 q133 q140 q142 q26 q49 q67 q31 q62; conv-30 q44 q52 q56
  q68 q71 q74 q78 q37 q22; conv-49 q96 q97 q99 q104 q123 q139 q141 q145.
- Other owner or contradicted (9): conv-26 q94 q76; conv-30 q67 q72 q9 q20; conv-49 q112
  q113 q152.
- Unrecorded detail (9): conv-26 q137 q138; conv-30 q21; conv-49 q102 q103 q133 q140 q142
  q72.

Replays: `runs/locomo-definitive-20260917/replay/audit-v1` (informed) and `audit-v1-blind`
in the engine worktree; they quote dataset text and are not committed.
