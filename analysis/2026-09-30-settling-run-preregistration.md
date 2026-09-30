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
