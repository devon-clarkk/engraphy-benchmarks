# Pending memory writes: the settling measurement

The Engraphy MCP server was unreachable on 2026-09-30 and 2026-10-01
(ECONNREFUSED on 127.0.0.1:8000), so these went unrecorded. Write them to
`proj-engraphy` when the server is back, additively, checking `outcome` and
resolving `needs_confirmation` in the same turn. Everything below is established;
nothing here depends on a measurement that has not happened.

## Node 1: the held-out split is now how the headline is measured

Decided 2026-09-30. Every LoCoMo lever was tuned or validated on conv-26,
conv-30 and conv-49: the retrieval width sweep, the reader replays for the
subject-and-occasion check, and the entity-roster analysis. Those three are the
seen split, and figures already published on them (66.8% strict, 86.1%
matched-convention, both at k=20) stay as what they are: measurements on the
conversations the levers were fitted to.

The headline is now measured on the held-out split: conv-41, conv-42, conv-43,
conv-44, conv-47, conv-48 and conv-50. 1,486 questions, 1,151 non-adversarial,
209 sessions, and no lever was fitted to any of it. Staged in
engraphy-benchmarks `config/locomo-next.json` with a test asserting the two
splits are disjoint and cover all ten conversations, and in
`analysis/2026-09-30-settling-run-preregistration.md` (commit 50852c5), written
before any number existed.

Lever rules, also fixed in advance: a lever enters the default only with an
identified mechanism and an effect larger than the spread between runs of one
configuration, at no significant adversarial cost. Retrieval width 25 is in by
owner decision. The entity roster is measured default-off; its own rule already
failed on the seen split (5 non-adversarial questions, p 0.46, no adversarial
cost). The source-turn layer is excluded: it gained 21 questions and lost 8
adversarial declines, and storing turns is a design non-goal. An extraction
change from the extraction agent is not yet delivered.

## Node 2: a usage cap during ingest was silently producing empty conversations

Found and fixed 2026-09-30, engine PR #31 (branch `bench/settle-20260930`, commit
e78240d). `LLMExtractor.extract` and `LLMAdjudicate.decide` caught `LLMError`,
which `QuotaExhausted` subclasses, so a capped extraction window returned an
empty result and a capped dedup band resolved `distinct`. `phase_ingest` then
checkpointed the conversation as done, and a resume skipped it.

Live evidence: with the CLI capped, conv-26 and conv-30 each ingested `0 drafts
-> 0 nodes` in 31 seconds, against 131 memories in about 10 minutes for conv-26
on 2026-09-17. Left alone the run would have scored 1,486 questions against a
store missing whole conversations and reported it as settled.

The fix propagates `QuotaExhausted` from extraction and adjudication, keeps every
other `LLMError` tolerant (one recorded gap, one counted fallback), and does not
checkpoint a conversation whose ingest stopped at a cap, so a resume clears the
partial scope and ingests it again. Five tests in
`bench/tests/test_quota_during_ingest.py`. The extraction agent fixed the same
defect independently on `feat/extraction-coverage`, so the two need reconciling
at handover.

Worth remembering beyond LoCoMo: any phase that treats a provider cap as a
per-item failure will silently produce a partial store. The answer and judge
phases already treated it as a clean stop; ingest did not.

## Node 3: how the published LoCoMo figures divide, verified from sources

Recorded 2026-09-30, full note in
`analysis/2026-09-30-how-the-leaders-measure.md`. Published LoCoMo figures sit in
two worlds. The Mem0 paper's 66.88 (arXiv:2504.19413) states its setup:
GPT-4o-mini answerer, mean of 10 runs, categories 1 to 4. Mem0's own 92.5
(mem0.ai/research) states no retrieval budget, no answerer or judge model, no
judge prompt, no run count. Zep self-reports 75.14% +/- 0.17 against the 65.99
Mem0 published for it, and Zep's own paper (arXiv:2501.13956) does not evaluate
on LoCoMo at all. Vendor figures in the 90s found by search are self-reported
with no stated methodology and are not used as comparators.

The high figures come from the conventions this repository reproduces verbatim
from `mem0ai/memory-benchmarks` at `4b61c5d`: a reader told never to decline, a
judge accepting one item of a multi-item gold answer with 14-day date and 50%
duration tolerance, adversarial excluded, and up to 200 memories in context.
Engraphy's engine returns at most 25 results by design, which is the most likely
source of a single-hop deficit under the strict convention: single-hop is one
fact in one turn and is 654 of the 1,151 held-out non-adversarial questions.
Multi-hop is where the leaders use graph or multi-strategy retrieval; Engraphy's
measured answer is the text-based entity roster, chosen because graph traversal
and a node-distance reranker were both measured as net losses.

## Node 4: an expired CLI session was being classified as a usage cap

Found and fixed 2026-10-01, engine PR #31 (branch `bench/settle-20260930`,
commit a182de1). `ClaudeCLIClient` read any `is_error` result it could not
recognise as a usage cap, so `"Failed to authenticate: OAuth session expired and
could not be refreshed"` raised `QuotaExhausted`. The supervisor's response to a
cap is correct and is the worst possible response to this: it slept 4.5 hours at
a time, for over ten hours, logging "usage limit" while nothing could have
succeeded. The reason it cost a day rather than a minute is that both the harness
log and the operator's reading of it agreed on the wrong cause.

The fix adds `AuthExpired(LLMError)`, matches the authentication wordings before
the usage ones at all three places the CLI result is classified, and gives
`stop_class` a third answer: `halt`. A halt prints the reason and exits for an
operator instead of waiting, because `claude login` is the only thing that clears
it, and an agent must not do it. Tests in `bench/tests/test_provider_auth.py`
fake `subprocess.run`, so they assert the classification with no CLI and no
sleeping.

General lesson: a stop class is a claim about what will fix the stop. Waiting,
relaunching and fetching an operator are three different claims, and a default
that collapses them to "wait" turns a one-minute fix into a lost day.

## Node 5: an A/B's wiring has to be asserted at the seam, not in the registry

Found 2026-10-01 while validating the two-arm extraction command before spending
a run on it, fixed in engine commit a2fdc34. `llm_wide` was registered correctly
(`EXTRACT_PROMPTS["llm_wide"] == "extract-wide.md"`), took its own scope and its
own arm_id, and had a test asserting all of that. But `_build_extractor` called
`LLMExtractor(client, pack)` without `prompt_name`, so the constructor default
`extract.md` applied and the wide arm ran the shipped prompt.

Nothing would have failed. Both arms would have ingested identical stores into
two scopes, coverage and accuracy would have come out equal, and the honest
reading of that result is "the wider prompt makes no difference", which would
have been recorded as a measured null and dropped the lever.

What the test was missing is the seam: it asserted the table that names the
prompt, not the object that loads it. The replacement asserts
`_build_extractor("llm_wide", pack).prompt_name` and that the two arms' system
prompts differ. Worth generalising to any A/B in this harness: assert that the
two arms differ in the thing under test, at the point where it is constructed,
before paying for the comparison.
