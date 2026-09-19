# LoCoMo: definitive results on PR #23 with levers 2 to 4

Date: 2026-09-18. Run `locomo-definitive-20260917`, completed 2026-09-17.

## Configuration

| | |
|---|---|
| engine | `devon-clarkk/engraphy` branch `bench/locomo-conventions-reader-width` at `3df1a4d232bbd9410d8e8e205f198c29ac83255e`: PR #23 head `99b38a5` (partial dates, attribute quarantine) plus levers 2 to 4. Clean tree. |
| arm | `llm-conversational/search_only/always_distinct/k20` |
| retrieval | `search_only`, 20 results, full detail. The width was chosen by a rule committed before measurement (`analysis/2026-09-16-levers-preregistration.md`, commit `32a4bf3`). |
| reader | `claude-opus-4-8`, stance `grounded`, reply contract `verify`, skill `sha256:c3b00290...` |
| extractor | `claude-opus-4-8` |
| judge | `claude-sonnet-5`, best of 3 (strict); one pass (reference conventions) |
| dataset | `locomo10.json`, sha256 `79fa87e9...`, conversations `conv-26`, `conv-30`, `conv-49`: 500 questions, 389 non-adversarial |
| embedder | profile `onnx-fp32`, nomic-embed-text-v1.5 at `e9b6763`, onnxruntime 1.29.0 |
| host | i5-11600K, 12 logical CPUs, 15.8 GB, Windows 11, Python 3.14.3, Postgres 16.14, pgvector 0.8.5, schema 0028, Claude Code CLI 2.1.252 |
| run path | `engraphy-public-levers/runs/locomo-definitive-20260917` (strict) and `.../reference` (reference conventions) |

The run spanned three usage caps and a machine restart. Every resume continued from the checkpoint: ingest, answers and verdicts were never repeated.

## 1. Strict figure, Engraphy's own conventions

The reader may decline; the judge requires every gold item. 500 of 500 answered and graded, no reader or judge errors. Per-pass judge instability 1 of 40. Write-yield 95.2% (318 of 334).

| category | Engraphy | Mem0 | Mem0g | Zep |
|---|---|---|---|---|
| **excluding adversarial** | **66.8% [62 to 71] (260/389)** | 66.88 | 68.44 | 65.99 |
| all five categories | 71.8% [68 to 76] (359/500) | | | |
| single-hop | 69.0% [62 to 75] (129/187) | 72.93 | 75.71 | 76.60 |
| multi-hop | 53.8% [43 to 64] (43/80) | 67.13 | 65.71 | 61.70 |
| temporal | **72.9% [63 to 81] (70/96)** | 55.51 | 58.13 | 49.31 |
| open-domain | **69.2% [50 to 84] (18/26)** | 51.15 | 47.19 | 41.35 |
| adversarial | 89.2% [82 to 94] (99/111) | not reported | not reported | not reported |

Comparator figures: Chhikara et al., arXiv:2504.19413, Table 1 (LLM-as-a-Judge), aligned to LoCoMo's
category numbers. Table 1's column headers do not name the categories they hold. The paper's
overall score (Table 2) is the question-weighted mean of the four categories, whose sizes differ
(282, 321, 96 and 841 questions), so each of the 24 ways to assign the four columns to the four
categories predicts a different overall. One assignment reproduces the published overall for all
five systems reported in both tables, to within 0.01 points; the next best misses by up to 1.06,
and reading the headers as the dataset names them misses by 1.8 to 9.7. Under it, the paper's
"Single-Hop" column holds LoCoMo multi-hop (category 1), "Multi-Hop" holds open-domain
(category 3) and "Open-Domain" holds single-hop (category 4); "Temporal" is category 2 either
way. Method and sources: `analysis/2026-09-19-locomo-open-domain-findings.md`, section 3 and
its source list, recorded in proj-engraphy as the Fable analysis node `d7c05bc3`.
Aligned, Engraphy leads on temporal reasoning and open-domain and trails on single-hop and
multi-hop; the overall comparison does not depend on the alignment.

## 2. Reference-convention figure, for comparability

The same run, every non-adversarial question read again from its saved retrieval envelope under the answer prompt and judge of `mem0ai/memory-benchmarks` at `4b61c5d` (vendored verbatim): the reader must commit, the judge accepts at least one gold item, dates within 14 days and durations within 50%.

| category | raw | floor | **defensible** | Mem0 | Mem0g | Zep |
|---|---|---|---|---|---|---|
| **excluding adversarial** | 88.9% (346/389) | 75.6% (294/389) | **86.1% [82 to 89] (335/389)** | 66.88 | 68.44 | 65.99 |
| single-hop | 85.0% | 77.5% | 80.7% (151/187) | 72.93 | 75.71 | 76.60 |
| multi-hop | 95.0% | 63.7% | 93.8% (75/80) | 67.13 | 65.71 | 61.70 |
| temporal | 90.6% | 79.2% | 89.6% (86/96) | 55.51 | 58.13 | 49.31 |
| open-domain | 92.3% | 84.6% | 88.5% (23/26) | 51.15 | 47.19 | 41.35 |

Comparator columns aligned to LoCoMo's category numbers as in section 1.

### How the raw figure was checked

- **Control A.** Engraphy's strict judge graded each of the 346 reference answers the reference judge accepted. It accepted 294 of them: the **floor**, answers correct under both rubrics.
- **Control B.** 60 accepted questions were each paired with the reference answer to a different question from the same conversation, wrong by construction. The reference judge accepted 6 (10%), the strict judge 1 (2%).
- **Confabulation adjustment.** A credit is removed when only the reference rules accept it **and** none of the question's LoCoMo evidence turns appears in the retrieved memory. That is the population where a commit-forcing reader can build an answer from context about the right person that never held the fact. **It removes 11 credits.** The 41 remaining reference-only credits had evidence in context and pass under rules the reference judge states literally, chiefly one gold item of several.
- **Evidence.** Where every or some evidence turn was retrieved, the reference judge accepted 94.5% (294 of 311). Where none was, it accepted 65.8% (50 of 76), and the strict judge 51.3% of those (39), because memories often restate a fact without quoting its turn.

**The defensible reference-convention figure is 86.1% [82 to 89] excluding adversarial, with 75.6% as the floor and 88.9% as the ceiling.** Multi-hop carries the widest spread (63.7% to 95.0%): the one-item rule accepts a partial list, which is a stated rule of the reference judge and the main reason that category rises.

## 3. Comparability, stated wherever the figures appear

- **Sample.** 3 of LoCoMo's 10 conversations. The published figures cover all 10.
- **Runs.** One run. The published figures are the mean of 10. Two runs of one configuration differed on 19.6% of questions (2026-09-16).
- **Models.** Claude Opus 4.8 reader and Claude Sonnet 5 judge. The published figures use a GPT-4o-mini reader.
- **Category alignment.** The Mem0 paper's Table 1 headers do not name the LoCoMo categories they hold. The comparisons here use the one assignment that reproduces the paper's published overall for all five systems (section 1, and `analysis/2026-09-19-locomo-open-domain-findings.md`); it is established by that arithmetic, not stated by the paper.
- **Zep.** The Zep column is Mem0's measurement of Zep, which Zep disputes.
- **Reconstruction.** The reference conventions are reproduced from the reference source with every difference recorded in the pass manifest; the reference harness itself was not run end to end.

## 4. What to publish

Lead with the per-category strict table, and state both figures with their configuration:

1. **66.8% excluding adversarial, under Engraphy's strict conventions**: the reader may decline and the judge requires every gold item. Level with Mem0's published 66.88.
2. **89.2% on adversarial questions**: the category the published comparisons exclude, where declining is the correct answer.
3. **86% excluding adversarial, measured under the reference harness conventions for comparability** (range 76% to 89%).
4. **Temporal reasoning: 72.9% strict against the best published 58.13, and open-domain: 69.2% strict against the best published 51.15.** Both clear their comparators under the stricter judge. Open-domain rests on 26 questions (interval 50 to 84), so it is a strong lead on this sample rather than a settled one. Single-hop and multi-hop trail.

The rule for public surfaces holds: level with the leaders, never ahead of them on a single scalar. The sample, run count and model differences above mean a higher point estimate does not establish a ranking. Temporal reasoning is the claim that survives every one of them.

## 5. Against earlier runs, paired per question

| | excluding adversarial | adversarial |
|---|---|---|
| public engine `67dd41a` (2026-09-16) | 60.2% to 66.8%, p 0.005 | 73.9% to 89.2%, p 0.0002 |
| never-drop only, k=10, previous reader | 65.0% to 66.8%, p 0.42 | 75.7% to 89.2%, p 0.001 |

Levers 3 and 4 together move the adversarial result measurably; their non-adversarial effect is within run churn. PR #23 still refuses 15 writes (9 cross-type supersede, 5 supersede band, 1 date): the supersede downgrade in never-drop is not yet on the public engine.
