# The settling measurement: scale and rules, fixed before measurement

Written 2026-09-30, before any run under this configuration produced a number.

## What is measured

Engine `devon-clarkk/engraphy` main at `a2943842ae84512935954c9675f2650194daf2a9`,
which carries the never-drop date port and attribute quarantine (PR #23), the
supersede downgrade (PR #27), and the subject-and-occasion reader check with the
`verify` reply contract and the per-arm search width (PRs #24, #25). Schema 0028.

Configuration: `config/locomo-next.json`. Arm
`llm-conversational/search_only/always_distinct/k25`, the shipped default at width
25. All ten LoCoMo conversations: 1,986 questions, 1,540 of them non-adversarial.

## Runs and the headline

Independent runs of the whole pipeline, ingest included, in order `A`, `B`, `C`.
The headline is the mean across completed runs, with the standard deviation and
each run's own figure beside it. A run is counted only when every one of its
questions is graded.

Two runs are the minimum for a mean; the third is run if the usage budget allows.
If a run is incomplete when reporting is due, it is reported as incomplete with
its phase named, and it is excluded from the mean rather than partially counted.

Per-question churn between two runs of one configuration was 19.6% on 2026-09-16,
so a difference smaller than the spread across runs is not a result. That applies
to every comparison below, including against the published figures.

## Arms

- **Primary: the shipped default**, roster off. This is the number to publish.
- **Measured, default off: the entity roster.** Envelopes are rebuilt from the
  same store with the roster and re-read by the same reader, graded by the same
  judge, so the comparison differs only in retrieval. It cannot move the primary
  figure. Its pre-registered rule and its first measurement are in
  `../engraphy-benchmarks-completeness/analysis/2026-09-25-retrieval-completeness-findings.md`.
- **Excluded: the source-turn layer.** Measured on 2026-09-25 to gain 21
  non-adversarial questions and lose 8 adversarial declines, a significant
  regression on the category where declining is the correct answer, and storing
  turns is a design non-goal.

## Reporting

Both figures, per category, with the corrected category alignment: the Mem0
paper's Table 1 columns are matched to LoCoMo's categories by the one assignment
that reproduces its published overall for all five systems
(`analysis/2026-09-19-locomo-open-domain-findings.md`). Under it, open-domain and
temporal are Engraphy's leads and single-hop and multi-hop its deficits.

The standing rule holds: level with the leaders on the scalar, never ahead of
them, unless the multi-run mean and its spread establish otherwise. Whatever the
mean comes to is what is reported, including a figure level with or below the
published ones.

## Addendum, 2026-09-30: the held-out split and the lever rules

Fixed before any run under this configuration produced a number.

### The split

Every lever was tuned or validated on `conv-26`, `conv-30` and `conv-49`: the
retrieval width sweep, the reader replays, and the entity-roster analysis all used
that store. Those three are the **seen** split.

The **held-out** split is the other seven conversations, `conv-41`, `conv-42`,
`conv-43`, `conv-44`, `conv-47`, `conv-48` and `conv-50`: 1,486 questions, 1,151 of
them non-adversarial, 209 sessions. No lever was fitted to any of it.

**The reported headline is measured on the held-out split.** Tuning and subset
validation may use the seen split, and figures already published on the seen split
stay as what they are: measurements on the conversations the levers were fitted to.

### The levers and how each is decided

| Lever | Status | Decided by |
|---|---|---|
| Retrieval width 25 | In the default | Owner decision, recorded 2026-09-19 |
| Entity-complete retrieval roster | Measured, default off | Its own pre-registered rule, already applied on the seen split: it gained 5 non-adversarial questions (p 0.46) and cost no adversarial declines, which did not pass to ship |
| Extraction improvement | Not yet delivered | Subset validation on the seen split first, then a held-out run only if it passes |
| Source-turn layer | Excluded | Measured to cost 8 adversarial declines, and storing turns is a design non-goal |

A lever is promoted into the default only when it clears both:

1. **Mechanism.** Why it helps is identified and stated, not inferred from the score.
2. **Evidence.** Its effect on the seen split is larger than the spread between runs
   of one configuration, and it costs no significant adversarial ground.

A lever that fails either is reported with its measured effect and kept off. A
lever whose result cannot be explained is investigated against how published
systems handle that dimension before any conclusion is drawn.
