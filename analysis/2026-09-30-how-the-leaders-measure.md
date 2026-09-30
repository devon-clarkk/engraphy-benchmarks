# How the published systems measure, and what that means for our deficits

Date: 2026-09-30. Gathered while the usage cap blocked measurement, to have the
comparison ready for the consolidated report. Every claim carries its source and
how firm it is.

## 1. Published LoCoMo figures sit in two different worlds

| Figure | System | Source | What it rests on |
|---|---|---|---|
| 66.88 overall | Mem0 | Chhikara et al., arXiv:2504.19413, Table 2 | GPT-4o-mini answerer, mean of 10 runs, categories 1 to 4, per-category table whose column headers do not name the categories they hold |
| 92.5 | Mem0 | mem0.ai/research | The page states the score and that LoCoMo has "1,540 questions 5 categories". It does not state the retrieval budget, the answerer or judge model, the judge prompt, the number of runs, or whether partial credit is given |
| 75.14 +/- 0.17 | Zep, self-measured | blog.getzep.com, "Lies, damn lies & statistics" | Zep's rerun after what it calls three implementation errors in Mem0's evaluation of Zep, against the 65.99 Mem0 published for it |
| 65.99 | Zep, as Mem0 measured it | arXiv:2504.19413 | Disputed by Zep, above |
| 90s | several vendors | vendor blogs and directories, found by search | Self-reported, methodology not stated in the material found. Treated as unverified and not used as a comparator |

The two worlds are a convention difference, not a capability difference. The
conventions behind the high figures are the ones this repository reproduces
verbatim from `mem0ai/memory-benchmarks` at `4b61c5d`: a reader told never to
decline, a judge that accepts one item of a multi-item gold answer with 14-day
date and 50% duration tolerance, adversarial excluded, and a retrieval budget of
up to 200 memories. That is why this repository reports two figures, and why the
comparable one is the matched-convention figure rather than the strict one.

Zep's own paper (arXiv:2501.13956) does not evaluate on LoCoMo at all; its
abstract reports DMR and LongMemEval. So the Zep column in any LoCoMo table is
either Mem0's measurement of Zep or Zep's own rerun, and both should be named as
such.

## 2. What the leaders do on the dimensions where we trail

**Single-hop, the largest category (654 of the 1,151 held-out non-adversarial
questions).** It is one factual span in one turn. The reference harness hands its
reader up to 200 memories; Engraphy's engine returns at most 25 results by design
(`_MAX_LIMIT`, design doc 02). On a question whose answer sits in one turn,
budget is close to a free win: if the memory is anywhere in the top 200 it is in
context. This is a structural difference in what each system puts in front of the
reader, and it is the most likely explanation of a single-hop deficit under the
strict convention. It is also why the width sweep mattered and why it saturates:
widening inside a 25-result cap cannot reach a memory the two search legs never
rank, which the flat-50 control in the 2026-09-25 completeness work showed
directly (67.4% coverage at fifty results against 66.9% at twenty-five).

**Multi-hop.** The published systems that lead this category do it with graph or
multi-strategy retrieval: Mem0-graph extracts entities and (source, relation,
destination) triplets and resolves them against existing nodes, and Zep builds a
temporally-aware knowledge graph over episodes, entities and edges. Engraphy's
measured answer to the same problem is the entity roster, which is a text filter
over the store's own `person` and `thing` registry rather than an edge walk,
chosen because a node-distance reranker and graph traversal were both measured as
net losses on multi-hop earlier (2026-08, and the reranker work before it). The
roster's first measurement gained 5 non-adversarial questions on the seen split
(p 0.46). Whether that is a real effect is what the held-out measurement is for.

## 3. What the benchmark itself cannot settle

Zep's critique of LoCoMo is worth carrying into the report, because it applies to
every figure in it: conversations average roughly 16,000 to 26,000 tokens, which
fits inside a modern context window; there are no knowledge-update questions; and
the dataset carries missing ground-truth answers, multimodal errors and speaker
attribution mistakes. Mem0's own 2026 material makes a similar point about data
quality and about the vendor disputes.

That is the case for reporting a per-category table with its conventions attached
rather than a single scalar, and for not claiming a rank from a point estimate.

## Sources

- Mem0 paper: https://arxiv.org/html/2504.19413v1
- Mem0 research page: https://mem0.ai/research
- Mem0 benchmark harness at the pinned commit: https://raw.githubusercontent.com/mem0ai/memory-benchmarks/4b61c5d31b9c668a12b4f5e78064248a02c82d2b/benchmarks/locomo/prompts.py
- Zep on Mem0's evaluation: https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/
- Zep / Graphiti paper: https://arxiv.org/abs/2501.13956
- Engraphy's own completeness measurement: `../engraphy-benchmarks-completeness/analysis/2026-09-25-retrieval-completeness-findings.md`
