# Methodology

How Engraphy's LoCoMo figures are produced, exactly what each one pins, and what
they can and cannot be compared with. Every statement here is checkable against
`config/locomo.json`, the committed manifests under `results/`, or the engine
source at the pinned commit.

## What LoCoMo measures

LoCoMo (Maharana et al., ACL 2024) is a set of ten long multi-session
conversations between two speakers, each with questions about what was said. A
memory system ingests a whole conversation, then answers its questions from
memory. Answers are graded against a gold answer.

The file carries 1,986 questions in five categories:

| category | in the file | graded as |
|---|---:|---|
| single-hop | 841 | judge, against gold |
| temporal-reasoning | 321 | judge, against gold |
| multi-hop | 282 | judge, against gold |
| open-domain-knowledge | 96 | judge, against gold |
| adversarial | 446 | by rule: correct if the system declines |

The adversarial questions ask about things the conversation never says. The
right answer is to decline, so they are graded on whether the system did, never
by the judge.

**Two denominators, both always reported.** Figures published for memory systems
usually exclude the adversarial category, which is why the number quoted in the
literature is 1,540 questions: 1,986 less 446. Engraphy's headline uses that same
convention, **excluding adversarial**, and every report also prints the overall
figure across all five categories. A comparison that does not say which
denominator it uses is not a comparison.

## The Engraphy pipeline

| stage | what runs | pinned as |
|---|---|---|
| ingest | Each session is read in windows. An LLM extractor turns the turns into typed memories against Engraphy's `conversational` pack and writes them through the engine's own write path, so de-duplication, schema validation and row-level security all apply. Speaker names are kept as they appear; they are never flattened to "user" and "assistant". The verbatim text of the turns a memory cites is kept in its body. | extractor `claude-opus-4-8`; pack file hashed in the manifest; confirm policy `always_distinct` |
| retrieve | The engine's hybrid search, in process: a lexical leg and a vector leg fused by reciprocal rank. No graph traversal, no reranker. | strategy `search_only`; embedder `nomic-embed-text-v1.5` on ONNX Runtime, revision pinned |
| read | A reader answers from the retrieved memory only, under Engraphy's shipped answer-discipline skill, in the `grounded` stance: an inference must be declared and sourced, and a question the memory does not support is answered with `INSUFFICIENT`. | reader `claude-opus-4-8`; skill file hashed in the manifest |
| judge | The judge sees the question, the gold answer and the candidate answer, nothing else: never the retrieved memory, the arm or the model that produced the answer. Each answer is graded three times and the majority verdict stands. | judge `claude-sonnet-5`, best of 3; prompt hashed in the manifest |

**One arm, fixed for every question.** The strategy is never chosen per question
or per category. The published arm is `llm-conversational/search_only/always_distinct`.

**The judge is from the same vendor as the reader.** Both are Claude models. The
judge's task is binary: do two short answers state the same fact. Each run
measures the judge's own instability by grading a sample twice
(`judge_calibration` in the manifest), so the noise floor of a figure is part of
the figure. Grading any system's answers with a different judge is supported by
`grade.py`; see [ADAPTERS.md](ADAPTERS.md).

## The question set

Each run covers three whole conversations, `conv-26`, `conv-30` and `conv-49`:
500 questions, of which 389 are non-adversarial. Ingest cost scales with
conversations rather than questions, since a question cannot be answered until
its entire conversation is in the store, so a run covers whole conversations
rather than a sample of questions from all ten.

Every figure is reported with a 95% Wilson interval. On 389 questions the
interval on the headline is roughly plus or minus five points, and the smaller
categories carry wider ones. Read the intervals, not only the point estimate.

## What is pinned

`config/locomo.json` is the complete configuration and `reproduce.py` reads
nothing else.

| | |
|---|---|
| engine | `devon-clarkk/engraphy` at a full commit SHA |
| dataset | `locomo10.json` by sha256, byte size and upstream commit |
| arm and conversations | as above |
| models | extractor, reader and judge by exact model id; judge passes |
| embedder | profile, model, revision, graph file, ONNX Runtime line |
| thresholds | de-duplication bands, resonance and briefing floors and read-time collapse, as the engine resolves them at runtime |
| database | image and schema version |

Each committed result additionally carries the engine's own manifest, with the
dataset digest it read, every prompt and pack hash, the band thresholds read
back from the live database, the models that actually served each role, and the
per-question verdicts; plus a `provenance.json` with the host, the runtime and
package versions, and the Postgres and pgvector versions.

## Which figure comes from which engine

| figure | run | engine | write path |
|---|---|---|---|
| 67.1% excluding adversarial | `fullrun-conv-20260809` | Engraphy development branch `bench/full-run` at `631e7be`, schema 0023 | partial dates such as `2026-05` are accepted and stored as written; a typed attribute that fails validation is moved to a `dropped` bucket and the memory is kept; a supersede that cannot complete, because the replacement is of a different type or bands against a third memory, is written as a plain new memory with the old one left active and the downgrade flagged |
| see [results/](results/README.md) | `fullrun-conv-20260916` | public `devon-clarkk/engraphy` at `67dd41a`, schema 0024 | dates must be complete ISO dates; a memory whose typed attribute fails validation is refused; a cross-type supersede is refused (`ValidationError`); a supersede whose replacement bands against a third memory is refused (`SupersedeUnresolvedBandError`) |

The prompts, the reader skill, the pack, the dataset, the arm, the models and the
judge are the same across both runs; the prompt and skill hashes match. The write
path is the difference. Each run's `ingest.jsonl` counts the extracted memories,
the memories stored, and every refusal by class, with the engine's message for a
sample of each.

## Comparing with other systems

Published LoCoMo figures for other memory systems, including Mem0 and Zep, come
from different harnesses. They differ from these runs along every axis that moves
the number:

- **Questions.** Some use all ten conversations, some a subset. Most exclude the
  adversarial category, but not all say so.
- **Reader.** The model that turns retrieved memory into an answer, and its
  prompt, is part of what is measured. Engraphy's runs use Claude Opus 4.8.
- **Extraction.** Where a system extracts facts with an LLM, that model sets a
  ceiling. Mem0's open-source server extracts with `gpt-4o-mini` by default,
  according to its own benchmark repository.
- **Judge.** Model, prompt and number of passes all change the verdicts. How
  lenient a judge template is remains an open question in the field; see for
  example [mem0ai/memory-benchmarks#10](https://github.com/mem0ai/memory-benchmarks/issues/10).
- **Metric.** The original LoCoMo paper reports token F1, not judged accuracy.

So a figure from another harness places Engraphy relative to that system; it does
not rank the two. Two things make a comparison tighter:

1. **Same judge.** `grade.py` grades any system's answers with the judge,
   prompt, majority rule and adversarial rule used here. That removes the judge
   as a variable.
2. **Same reader.** Answering with the same reader model and a neutral prompt
   isolates the memory itself. `grade.py` records the reader as the submitter
   declares it.

The strongest comparison is a system run under a harness Engraphy does not
control. Engraphy's scoping request to the most widely used open suite is
[mem0ai/memory-benchmarks#26](https://github.com/mem0ai/memory-benchmarks/issues/26).

## Licensing

The code here is Apache-2.0. The engine it runs is fetched separately and is
licensed under the Business Source License 1.1. LoCoMo is CC BY-NC 4.0 and is
downloaded from its authors by `scripts/fetch_locomo.py`, never committed here.
Committed results carry question ids, categories, verdicts and the system's
answers, and no question text, gold answers or conversation text;
`scripts/rejoin.py` restores those from your own copy for auditing. See
[NOTICE](NOTICE).
