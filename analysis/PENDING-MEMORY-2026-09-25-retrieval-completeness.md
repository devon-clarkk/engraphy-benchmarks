# Pending write to Engraphy memory (scope proj-engraphy)

The Engraphy MCP server at 127.0.0.1:8000 refused connections on 2026-09-25, so
this node could not be written. Write it when the server is up, then delete this
file. Check the `outcome`; resolve `needs_confirmation` as `distinct`.

---

**type:** note
**scope:** proj-engraphy
**title:** Retrieval completeness measured 2026-09-25: the entity roster is safe but unproven, the source-turn backstop breaks the adversarial guard

**body:**

Measured 2026-09-25 against the kept store of run locomo-definitive-20260917 (318 memories, conv-26/30/49). Prototype on devon-clarkk/engraphy branch feat/entity-complete-retrieval (bdc6c17, 76ee47d, 442932d), pushed, not merged. Decision rules committed before any reader call: engraphy-benchmarks branch analysis/retrieval-completeness, commit fbbf1a5. Full writeup analysis/2026-09-25-retrieval-completeness-findings.md; engine spec design/analysis/retrieval-completeness.md.

THE TWO ADDITIONS. (1) Entity roster: when a question names a person or thing in the store's own person/thing registry, add every other active memory whose title or body names it, titles and attrs only, most query-similar first, capped at 100. Text filter, no edges walked, because traverse was already measured as a net loss on multi-hop. (2) Source-turn backstop: the conversation's raw turns as a second non-lossy layer, top 10 by the engine's own hybrid arithmetic, skipping turns already quoted in a retrieved memory.

RETRIEVAL COVERAGE, NO LLM (bench/completeness_recall.py; its k=20 arm reproduced 498 of the run's 500 saved envelopes id for id). Share of non-adversarial questions with ALL evidence in context: k=20 66.2%, k=25 66.9%, +roster 71.1%, +turns 80.1%, +both 84.2%. The width control matters most: unfiltered top-50 reached only 67.4%, because both hybrid legs cap at 30 candidates before fusion, so widening cannot reach a memory whose wording does not resemble the query. The gain is the mechanism, not more results.

READER ACCURACY, three arms over all 500 questions, definitive reader and strict judge, paired against a fresh k=25 control. Roster alone: non-adversarial 266 to 271 (+5, p=0.46), multi-hop 45 to 51 (+10/-4, p=0.18), adversarial 99 to 101. Roster plus turns: non-adversarial 292/389 = 75.1% (+26 vs control, p=0.0002), single-hop 129 to 146, but adversarial 99 to 93; the turns' own effect measured against roster-only is +21 non-adversarial (p=0.0025) and -8 adversarial (p=0.02). Re-read churn floor: k=20 to k=25 on the same store moved 22 verdicts both ways for net +6 (p=0.29), about 5% of verdicts flipping with retrieval held constant.

VERDICT UNDER THE PRE-REGISTERED RULES: neither ships. The roster is adversarially safe and its effect is inside this sample's noise. The backstop's gain is real and so is its regression.

WHY ADVERSARIAL INFLATED, worth keeping: the seven lost adversarial questions are all misattribution traps (what Caroline said when Melanie said it; what Jon wanted for Gina's store; what Sam limited when it was Evan). Six of seven reader CHECK lines cite a source turn; the seventh cites a baseline result and is churn. A raw turn carries the words without the speaker attribution a typed memory's title supplies. Decline rates show the same shift on both populations: the backstop cut non-adversarial declines 43 to 24 and adversarial declines 99 to 93, while the roster left both untouched (43, and 99 to 101).

FAILURE-CLASS RECOVERY (questions the definitive run got wrong, now correct): single-hop evidence-never-extracted 34 questions, 1 in the control to 18 with turns; multi-hop evidence-stored-but-not-retrieved 12 questions, 1 to 3 with the roster; multi-hop evidence-already-complete 13 questions, 2 to 7 with the roster. Each mechanism moves its own class, and no read-path change moves an extraction gap.

WHAT TO DO. Roster: build as an engine search option (entity_roster flag, roster_limit, additive envelope keys entities and entity_roster), default off, and measure it on the staged ten-conversation run as a second arm over the same ingest, because its claim is multi-hop-specific and that run has 282 multi-hop questions against 80 here. Turns: do not build yet. It needs the product decision first, since design/01-core-data-model.md lists storing transcripts as a non-goal, and then an attribution fix making the speaker a first-class field the reader must check. Neither belongs in the staged run as harness-only code: a harness-only retrieval path is a configuration no deployment can reproduce.
