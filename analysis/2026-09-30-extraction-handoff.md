# Handoff: the `llm_wide` extraction arm

For the benchmark session running the consolidated held-out LoCoMo run.

**Gate: do not fold this in yet.** The change is built, tested and ready to
measure, but its subset validation has not run: the account has been at the usage
cap since the ingest was launched. Section 4 is the gate. Nothing below should
enter the final run until section 4 reports a pass, and I will report that number
when it exists.

## 1. What it is

One extraction prompt, offered as a separate extractor name. The shipped
`bench/prompts/extract.md` is **byte-identical to main** (`b7fdf557f7f60a9c`, the
hash the definitive run recorded), so the default ingest is unchanged and your
existing arm behaves exactly as before.

| | |
|---|---|
| Branch | `devon-clarkk/engraphy` `feat/extraction-coverage`, head `64dbd51`, pushed, not merged |
| New prompt | `bench/prompts/extract-wide.md`, sha256 `2f3fa4c9e6c1a457` |
| New extractor | `llm_wide` (`EXTRACT_PROMPTS` in `bench/core/run.py`) |
| Engine files touched | none |
| Tests | `bench/tests/test_extract_quota.py`, 5 tests |

## 2. How to enable it

Add one arm. The arm string is the whole of the change:

```
--arm llm_wide-conversational:search_only:k=25
```

which parses to arm id
`llm_wide-conversational/search_only/always_distinct/k25`.

In `config/locomo-next.json` that is a second entry beside the existing
`llm-conversational:search_only:k=25`, not a replacement.

Three things worth knowing before you budget it:

- **It is a separate ingest, not a second read over the same store.** The scope
  is `hs-<conv>-llm_wide`, distinct from `hs-<conv>-llm`, so the arm costs a full
  extraction pass over every conversation in addition to reading and judging.
  This is unlike a `k=` variant, which shares ingest.
- **Expect a larger store.** The change exists to draft more memories. The
  pre-registered bloat guard is three times the control; if it exceeds that,
  that is a reported failure, not something to accept quietly.
- **Both prompt hashes are recorded** in the run manifest under
  `prompt_hashes`, so a run using the arm is self-describing.

## 3. Port this regardless of the arm

`3cf6699` on the same branch fixes a defect that affects **your run whether or
not you take the extraction change**.

`QuotaExhausted` subclasses `LLMError`, and `LLMExtractor.extract` caught
`LLMError` broadly and returned an empty window. A usage cap during ingest was
therefore recorded as "this window contributed nothing" for every window: the run
logged `0 drafts -> 0 nodes` per conversation, wrote `done: true`, and exited 0
with an empty store. I hit exactly this on 2026-09-30, and the run looked
successful.

Your staged configuration is three full runs over ten conversations, so its
ingest phase is long and near-certain to meet a cap. Without this fix a capped
ingest yields a silently empty store and a run that reports success. The fix
propagates `QuotaExhausted` to the run loop that already knows how to checkpoint
and resume; three tests cover it.

## 4. The gate

Run on the **seen** conversations only (conv-26, conv-30, conv-49). The held-out
seven are untouched by this work and stay that way, so your final number is
measured on conversations the prompt was never checked against.

```
scripts/validate_extraction.sh          # both arms, one run, resumable
```

It ingests `llm` and `llm_wide` side by side in one run (same engine, same
models, same dedup policy, differing only in the prompt) and then runs
`bench.extraction_coverage`, which needs no LLM.

Pre-registered pass conditions
(`analysis/2026-09-30-extraction-coverage-preregistration.md`): at least 40% of
the 46 extraction-gap questions recovered into the store, overall evidence recall
not falling, and store growth within three times the control.

**Passing that gate still does not mean it ships.** Coverage is not accuracy, and
more memories about a named person is the condition that cost 8 adversarial
declines in the retrieval work on 2026-09-25. A reader and judge pass over both
arms including all 111 adversarial questions is required first, with adversarial
not falling by more than 3 net.

## 5. Why it is worth your ingest budget

Measured on the definitive store with no LLM (`bench.extraction_coverage`,
`runs/coverage-base.json`):

| | |
|---|---|
| Memories | 317, from 1,297 turns |
| Questions whose evidence is **held anywhere in the store** | 71.6% |
| Questions with **all evidence retrieved** into context at k=25 | 66.9% |

Retrieval gives up about 5 points against what the store holds. Extraction gives
up **28 points** before retrieval is even asked. That is the largest single
honest lever left on this benchmark, and it is why an extra ingest pass is
defensible.
