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

## Addendum, 2026-10-01: how the wider extraction prompt is decided

Fixed before the arm has been ingested once. `llm_wide` is `llm` with
`bench/prompts/extract-wide.md` in place of `extract.md`: completeness over
economy, what one person says to or about another in scope with both named, and a
new instance of a recurring thing treated as a new fact.

### Why this lever needs a replicate and the others did not

Retrieval levers are deterministic given a store: the roster and the width sweep
were replayed against one ingest, so their spread is the reader's, already
measured. Extraction changes the store, and extraction is a model call, so two
ingests of the *same* prompt differ. Comparing one `llm` ingest against one
`llm_wide` ingest therefore cannot separate the prompt from the draw.

So stage 1 ingests three stores on the seen split: `llm`, `llm_wide`, and a
second `llm` under its own run id. The `llm`-against-`llm` pair is the noise
floor, measured rather than assumed, and it costs no reader or judge calls.

### The order, and the gate

1. Ingest all three stores.
2. **Store coverage**, no model in the loop: for each question, is the evidence
   the benchmark cites present in any stored memory of that scope? This is the
   ceiling on what any read path could surface, and `llm_wide` has to move it to
   be worth anything. Store size is reported beside it.
3. **The gate.** The answer and judge pass on the two arms is paid for only if
   the coverage gain of `llm_wide` over `llm` both exceeds the `llm`-to-`llm`
   replicate difference and reaches p < 0.05 on an exact McNemar test over the
   paired per-question coverage outcomes. A gain inside the replicate spread
   drops the lever at this step, on the stated mechanism ground that a prompt
   which does not change what is stored cannot change what is answered.
4. If the gate opens, answers and judging run on both arms, same reader, same
   strict judge, paired per question.

### What promotion requires

Beyond the two standing conditions, mechanism and evidence:

- **Coverage.** The gain survives the replicate comparison above.
- **Accuracy.** The judged gain on the 389 non-adversarial seen questions exceeds
  the between-run churn already measured on this split, which is where the lever
  3 and 4 attribution landed: an adversarial move of 75.7% to 89.2% was
  significant at p 0.0013, while the non-adversarial move sat at p 0.42 and was
  reported as churn. A gain of that second kind is churn here too.
- **No adversarial cost.** The adversarial decline rate does not fall
  significantly. A wider prompt stores more, and more stored text is more for an
  adversarial question to look true against, so this is the specific risk the
  lever carries and it is checked rather than assumed.
- **Store cost is reported either way**, as nodes per conversation against `llm`.
  Coverage bought by storing everything is recorded as such.

### A note on what makes this checkable

Each arm's manifest records the prompt its extractor loaded, by name and hash,
per arm (`extract_prompts`). The run-wide `prompt_hashes` block lists every
prompt in the tree and so reads identically whichever arm selected which, which
is not enough for a third party to confirm the two arms differed in the thing
under test.

## Addendum, 2026-10-02: the lever verdict and how the held-out runs are allocated

Fixed before the held-out runs were launched, and before any held-out question
had been answered under this configuration.

### `llm_wide` is promoted into the combined engine

It cleared every condition of the rule above, measured on the seen split:

- **Mechanism.** It stores the evidence the shipped prompt discards. Store
  coverage, with no model in the loop, went from 73.4% to 85.8% of 387 scorable
  questions, discordant 5 against 53: it holds the cited evidence for 53
  questions the control dropped and loses 5 the control kept. On the labelled
  extraction-gap set, 9 of 46 recovered became 28 of 46.
- **Coverage, against a measured floor.** A second ingest of the shipped prompt
  came to 72.6%, so the floor is 0.8 points, discordant 22 against 19, p 0.76.
  The lever's +12.4 points sits far outside it at p < 0.0001.
- **Accuracy.** Judged non-adversarial accuracy went from 69.15% to 76.61% of
  389 questions, discordant 9 against 38, p 0.000025. Every category rose:
  multi-hop 57.5 to 61.25, open-domain 69.23 to 76.92, single-hop 69.52 to
  78.61, temporal 78.12 to 85.42.
- **No adversarial cost.** 88.29% both ways on 111 adversarial questions,
  discordant 3 against 3, p 1.0. This was the specific risk a wider store
  carries, and it did not materialise.
- **Cost, reported.** 515 memories against 333, so +55%, and about 50% longer to
  ingest.

The entity-complete roster stays measured and default off: its own rule failed on
the seen split. The source-turn layer stays excluded. Retrieval width 25 is in by
owner decision. So the combined engine for the held-out runs is width 25 plus the
wide extraction prompt.

### The held-out runs

Run A carries two arms, the combined engine and the shipped extraction prompt, on
one ingest. That measures the lever's isolated effect out of sample as well,
rather than only on the split it was validated against, and a lever that gains
7.46 points in validation and nothing on held-out data is a result worth having
rather than one to avoid asking for.

Run B carries the combined engine alone. Two runs of one configuration are what
the spread of the headline needs, and that spread is the figure the standing rule
compares any claim of a lead against.

The reported headline is the combined engine's mean across the runs, on the seven
held-out conversations, with the spread stated beside it. The matched-convention
pass runs on each strict run, as before.
