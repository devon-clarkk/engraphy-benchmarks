# Benchmarking another memory system

Any memory system can be scored here with the judge, prompt, best-of-3 majority,
adversarial rule and intervals that scored Engraphy. The integration point is a
file of answers.

## The answers contract

One JSON object per line:

```json
{"question_id": "conv-26:q0", "answer": "She moved there in 2019."}
```

- `question_id` is `{sample_id}:q{j}`, where `j` is the 0-based position of the
  question in that conversation's `qa` list in `locomo10.json`. It is the id the
  engine's loader assigns, and the one every committed result uses.
- `answer` is your system's answer as it would reach a user. To decline, answer
  `INSUFFICIENT`, or any phrasing the abstention rule recognises; the adversarial
  category is graded on whether the system declined.
- Include every question of every conversation you cover. A question with no row
  is graded wrong. It is never treated as a correct abstention, so partial
  coverage cannot raise a score.

To match the conversations Engraphy's figures use, cover `conv-26`, `conv-30` and
`conv-49`.

## Grading

```bash
python grade.py answers.jsonl --system my-memory-system
```

The first run clones the pinned engine, builds its virtualenv and downloads the
dataset, because the judge, the prompt and the scoring are imported from the
engine checkout rather than copied. Grading is checkpointed per question; run the
same command again to resume.

It writes, under `graded/my-memory-system/`:

- `graded.jsonl`: one verdict per question, with the best-of-3 tally. It carries
  the judge's reasoning, which quotes the dataset, so `graded/` is not committed.
- `summary.json`: overall and excluding-adversarial accuracy, every category,
  95% Wilson intervals, the judge model and prompt hash, the engine commit, the
  dataset digest and the sha256 of your answers file.

To publish a graded result, commit `summary.json`, and a redacted copy of
`graded.jsonl` made with `scripts/redact_run.py`.

## What to state beside a graded figure

A graded figure is only as comparable as its reader. Record, next to it:

- the reader model and its prompt;
- the extraction model, if your system extracts facts with an LLM;
- which conversations you covered;
- whether retrieval or reading used anything beyond the conversation itself.

Answering with the reader and prompt Engraphy's runs use isolates the memory
system as the only difference. [METHODOLOGY.md](METHODOLOGY.md) lists the axes
along which harnesses differ.

## Checking the grader against Engraphy's own run

`scripts/answers_from_run.py` turns an Engraphy harness run into this answers
format, so the same answers can go through `grade.py` and be compared with the
verdicts the harness recorded. Agreement is bounded by the judge instability each
run measures, and that figure is in the run's manifest.

## Running another system through the full pipeline

The engine's harness keeps its ingest and retrieval seams in the engine
repository (`bench/core/ingest.py`, `bench/core/retrieve.py`), written against
Engraphy's engine. Running another backend through Engraphy's extractor and
reader would use a backend-neutral seam there, with this repository pinning it,
so there is still exactly one harness. The answers contract above is the
integration point available today.
